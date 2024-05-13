# Copyright (c) 2020 Cloudbase Solutions Srl
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Command-line interface sub-commands related to services.
"""

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter


class ServiceFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Host",
               "Binary",
               "Topic",
               "Enabled",
               "Status",
               "Mapped Region IDs",
               "Created At",
               "Last Updated At")

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.host,
                obj.binary,
                obj.topic,
                obj.enabled,
                obj.status,
                obj.mapped_regions,
                obj.created_at,
                obj.updated_at)
        return data


def _add_service_enablement_args_to_parser(parser):
    """ Adds an arg group for mutually exclusive --enabled/--disabled args. """
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--enabled', action='store_true', dest='enabled',
                       default=None, help="Mark service as enabled.")
    group.add_argument('--disabled', action='store_false', dest='enabled',
                       default=None, help="Mark service as disabled.")


class CreateService(show.ShowOne):
    """ Creates a new service. """
    def get_parser(self, prog_name):
        parser = super(CreateService, self).get_parser(prog_name)

        parser.add_argument('--host', required=True,
                            help='A hostname/IP for the new service.')
        parser.add_argument('--binary', required=True,
                            help='The service binary for the ew service.')
        parser.add_argument('--topic', required=True,
                            help='The messaging topic for the new service.')
        parser.add_argument('--coriolis-region', action='append',
                            dest='regions', default=[],
                            help="ID of a region the service should be "
                            "associated with. Can be supplied multiple times.")
        _add_service_enablement_args_to_parser(parser)

        return parser

    def take_action(self, args):
        service = self.app.client_manager.coriolis.services.create(
            args.host, args.binary, topic=args.topic, enabled=args.enabled,
            regions=args.regions)

        return ServiceFormatter().get_formatted_entity(service)


class UpdateService(show.ShowOne):
    """ Updates a service. """
    def get_parser(self, prog_name):
        parser = super(UpdateService, self).get_parser(prog_name)

        parser.add_argument('id', help='The service\'s ID.')
        parser.add_argument('--coriolis-region', action='append',
                            dest='regions', default=[],
                            help="ID of a region the service should be "
                                 "associated with. Can be supplied multiple "
                                 "times. Update will override all existing "
                                 "region associations with the one(s) provided"
                                 " if at least one region is given.")
        _add_service_enablement_args_to_parser(parser)

        return parser

    def take_action(self, args):
        updated_values = {}
        if args.enabled is not None:
            updated_values['enabled'] = args.enabled
        if args.regions is not None:
            updated_values["mapped_regions"] = args.regions
        service = self.app.client_manager.coriolis.services.update(
            args.id, updated_values)

        return ServiceFormatter().get_formatted_entity(service)


class ShowService(show.ShowOne):
    """ Show details for a service. """

    def get_parser(self, prog_name):
        parser = super(ShowService, self).get_parser(prog_name)
        parser.add_argument('id', help='The service\'s id.')
        return parser

    def take_action(self, args):
        service = self.app.client_manager.coriolis.services.get(
            args.id)
        return ServiceFormatter().get_formatted_entity(service)


class DeleteService(command.Command):
    """ Delete a service. """

    def get_parser(self, prog_name):
        parser = super(DeleteService, self).get_parser(prog_name)
        parser.add_argument('id', help='The service\'s id.')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.services.delete(args.id)


class ListServices(lister.Lister):
    """ List all services. """

    def get_parser(self, prog_name):
        parser = super(ListServices, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        service_list = self.app.client_manager.coriolis.services.list()
        return ServiceFormatter().list_objects(service_list)

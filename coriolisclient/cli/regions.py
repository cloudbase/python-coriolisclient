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
Command-line interface sub-commands related to regions.
"""

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter


class RegionFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Name",
               "Enabled",
               "Description",
               "Mapped Endpoint IDs",
               "Mapped Service IDs",
               "Created At",
               "Last Updated At")

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.name,
                obj.enabled,
                obj.description or "",
                obj.mapped_endpoints,
                obj.mapped_services,
                obj.created_at,
                obj.updated_at)
        return data


def _add_region_enablement_args_to_parser(parser):
    """ Adds an arg group for mutually exclusive --enabled/--disabled args. """
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--enabled', action='store_true', dest='enabled',
                       default=None, help="Mark region as enabled.")
    group.add_argument('--disabled', action='store_false', dest='enabled',
                       default=None, help="Mark region as disabled.")


class CreateRegion(show.ShowOne):
    """ Creates a new region. """
    def get_parser(self, prog_name):
        parser = super(CreateRegion, self).get_parser(prog_name)

        parser.add_argument('name',
                            help='A name for the new region.')
        parser.add_argument('--description', default="",
                            help='A description for the new region.')
        _add_region_enablement_args_to_parser(parser)

        return parser

    def take_action(self, args):
        region = self.app.client_manager.coriolis.regions.create(
            args.name, description=args.description, enabled=args.enabled)

        return RegionFormatter().get_formatted_entity(region)


class UpdateRegion(show.ShowOne):
    """ Updates a region. """
    def get_parser(self, prog_name):
        parser = super(UpdateRegion, self).get_parser(prog_name)

        parser.add_argument('id', help='The region\'s ID.')
        parser.add_argument('--name',
                            help='New name for the region.')
        parser.add_argument('--description', default="",
                            help='New description for the region.')
        _add_region_enablement_args_to_parser(parser)

        return parser

    def take_action(self, args):
        updated_values = {}
        if args.enabled is not None:
            updated_values["enabled"] = args.enabled
        if args.name:
            updated_values["name"] = args.name
        if args.description:
            updated_values["description"] = args.description
        region = self.app.client_manager.coriolis.regions.update(
            args.id, updated_values)

        return RegionFormatter().get_formatted_entity(region)


class ShowRegion(show.ShowOne):
    """ Show details for a region. """

    def get_parser(self, prog_name):
        parser = super(ShowRegion, self).get_parser(prog_name)
        parser.add_argument('id', help='The region\'s id.')
        return parser

    def take_action(self, args):
        region = self.app.client_manager.coriolis.regions.get(
            args.id)
        return RegionFormatter().get_formatted_entity(region)


class DeleteRegion(command.Command):
    """ Delete a region. """

    def get_parser(self, prog_name):
        parser = super(DeleteRegion, self).get_parser(prog_name)
        parser.add_argument('id', help='The region\'s id.')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.regions.delete(args.id)


class ListRegions(lister.Lister):
    """ List all regions. """

    def get_parser(self, prog_name):
        parser = super(ListRegions, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        region_list = self.app.client_manager.coriolis.regions.list()
        return RegionFormatter().list_objects(region_list)

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

import argparse

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter


class LicensingStatusFormatter(formatter.EntityFormatter):

    def __init__(self):
        self.columns = [
            "appliance_id",
            "earliest_licence_expiry_time",
            "latest_licence_expiry_time",
            "current_performed_migrations",
            "current_performed_replicas",
            "current_available_migrations",
            "current_available_replicas",
            "lifetime_perfomed_migrations",
            "lifetime_perfomed_replicas",
            "lifetime_available_migrations",
            "lifetime_available_replicas",
        ]

    def _get_formatted_data(self, obj):
        data = [obj.appliance_id,
                obj.earliest_licence_expiry_time,
                obj.latest_licence_expiry_time,
                obj.current_performed_migrations,
                obj.current_performed_replicas,
                obj.current_available_migrations,
                obj.current_available_replicas,
                obj.lifetime_perfomed_migrations,
                obj.lifetime_perfomed_replicas,
                obj.lifetime_available_migrations,
                obj.lifetime_available_replicas,
                ]

        return data


class LicenceFormatter(formatter.EntityFormatter):
    columns = ("ID",
               "Issue Date",
               "Migrations",
               "Replicas",
               "Period Start",
               "Period End",
               "Licence Version",
               )

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.period_end)

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.issue_date,
                obj.migrations,
                obj.replicas,
                obj.period_start,
                obj.period_end,
                obj.licence_version,
                )

        return data


class LicensingStatus(show.ShowOne):
    """ Retrieves Licensing Status """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('appliance_id', help="The appliance ID")
        return parser

    def take_action(self, args):
        lic_status = self.app.client_manager.coriolis.licensing.status(
            args.appliance_id)
        return LicensingStatusFormatter().get_formatted_entity(lic_status)


class LicenceRegister(show.ShowOne):
    """ Registers a Coriolis Licence """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('appliance_id', help="The appliance ID")
        licence_group = parser.add_mutually_exclusive_group(required=True)
        licence_group.add_argument('--licence-pem',
                                   help="PEM formatted licence")
        licence_group.add_argument('--licence-pem-file',
                                   type=argparse.FileType('r'),
                                   help='Relative/full path to a file '
                                        'containing the PEM formatted licence')
        return parser

    def take_action(self, args):
        pem = None
        raw_arg = getattr(args, 'licence_pem')
        file_arg = getattr(args, 'licence_pem_file')
        if raw_arg:
            pem = raw_arg
        elif file_arg:
            with file_arg as fin:
                pem = fin.read()

        if not pem:
            raise ValueError('No licence-pem[-file] parameter provided.')

        licence = self.app.client_manager.coriolis.licensing.register(
            args.appliance_id, pem)
        return LicenceFormatter().get_formatted_entity(licence)


class LicenceList(lister.Lister):
    """ Retrieves Licence list """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('appliance_id', help="The appliance ID")
        return parser

    def take_action(self, args):
        lic_list = self.app.client_manager.coriolis.licensing.list(
            args.appliance_id)
        return LicenceFormatter().list_objects(lic_list)


class LicenceShow(show.ShowOne):
    """ Retreieves information about licence """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('appliance_id', help='The appliance ID')
        parser.add_argument('licence_id', help='The ID of the licence')
        return parser

    def take_action(self, args):
        licence = self.app.client_manager.coriolis.licensing.show(
            args.appliance_id, args.licence_id)
        return LicenceFormatter().get_formatted_entity(licence)


class LicenceDelete(command.Command):
    """ Deletes a licence """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('appliance_id', help='The appliance ID')
        parser.add_argument('licence_id', help='The ID of the licence')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.licensing.delete(
            args.appliance_id, args.licence_id)

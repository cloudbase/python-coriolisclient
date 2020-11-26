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

from cliff import lister
from cliff import show

from coriolisclient.cli import formatter


class ApplianceFormatter(formatter.EntityFormatter):
    columns = ["ID"]

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.id)

    def _get_formatted_data(self, obj):
        data = [obj.id]
        return data


class ApplianceList(lister.Lister):
    """ Retrieves a list of registered appliance IDs """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser

    def take_action(self, args):
        app_list = self.app.client_manager.coriolis.licensing_appliances.list()
        return ApplianceFormatter().list_objects(app_list)


class ApplianceShow(show.ShowOne):
    """ Retrieves appliance information """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('appliance_id', help='The appliance ID')
        return parser

    def take_action(self, args):
        appliance = self.app.client_manager.coriolis.licensing_appliances.show(
            args.appliance_id)
        return ApplianceFormatter().get_formatted_entity(appliance)


class ApplianceCreate(show.ShowOne):
    """ Creates an Appliance """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser

    def take_action(self, args):
        appliance = \
            self.app.client_manager.coriolis.licensing_appliances.create()
        return ApplianceFormatter().get_formatted_entity(appliance)

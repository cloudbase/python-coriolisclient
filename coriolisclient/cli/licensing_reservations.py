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


class ReservationFormatter(formatter.EntityFormatter):
    columns = ("ID",
               "Appliance ID",
               "Licence ID",
               "Type",
               "Count",
               "Created At",
               )

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.appliance_id,
                obj.licence_id,
                obj.type,
                obj.count,
                obj.created_at,
                )

        return data


class ReservationList(lister.Lister):
    """ Retrieves a list of reservations """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('appliance_id', help="The appliance ID")
        return parser

    def take_action(self, args):
        res_list = \
            self.app.client_manager.coriolis.licensing_reservations.list(
                args.appliance_id)
        return ReservationFormatter().list_objects(res_list)


class ReservationShow(show.ShowOne):
    """ Retrieves information about a reservation """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('appliance_id', help='The appliance ID')
        parser.add_argument('reservation_id', help='The reservation ID')
        return parser

    def take_action(self, args):
        res = self.app.client_manager.coriolis.licensing_reservations.show(
            args.appliance_id, args.reservation_id)
        return ReservationFormatter().get_formatted_entity(res)


class ReservationRefresh(show.ShowOne):
    """ Refreshes a reservation """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('appliance_id', help='The appliance ID')
        parser.add_argument('reservation_id', help='The reservation ID')
        return parser

    def take_action(self, args):
        res = self.app.client_manager.coriolis.licensing_reservations.refresh(
            args.appliance_id, args.reservation_id)
        return ReservationFormatter().get_formatted_entity(res)

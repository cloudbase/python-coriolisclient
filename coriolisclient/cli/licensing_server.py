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


class ServerStatusFormatter(formatter.EntityFormatter):
    columns = [
        "Hostname", "Multi-appliance",
        "Supported Licence Versions", "Server Time"]

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.hostname)

    def _get_formatted_data(self, obj):
        data = [
            obj.hostname,
            obj.multi_appliance,
            obj.supported_licence_versions,
            obj.server_local_time]
        return data


class ServerStatus(show.ShowOne):
    """ Retrieves licensing server information """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser

    def take_action(self, args):
        status = self.app.client_manager.coriolis.licensing_server.status()
        return ServerStatusFormatter().get_formatted_entity(status)

# Copyright (c) 2017 Cloudbase Solutions Srl
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
import json

from cliff import lister
from coriolisclient.cli import formatter


class EndpointDestinationOptionFormatter(formatter.EntityFormatter):

    columns = ("Option Name",
               "Possible Values",
               "Configuration Default")

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.name)

    def _get_formatted_data(self, obj):
        data = (obj.name,
                obj.values,
                obj.to_dict().get("config_default"))
        return data


class ListEndpointDestinationOptions(lister.Lister):
    """ List endpoint destination environment options. """

    def get_parser(self, prog_name):
        parser = super(ListEndpointDestinationOptions, self).get_parser(
            prog_name)
        parser.add_argument('endpoint', help='The endpoint\'s id')
        parser.add_argument('--environment',
                            help='JSON encoded endpoint environment data')
        parser.add_argument(
            '--options', help="Names of parameters to get options for.",
            nargs='+', default=[])
        return parser

    def take_action(self, args):
        if args.environment:
            environment = json.loads(args.environment)
        else:
            environment = None

        options = []
        if args.options:
            options = args.options

        endpoints = self.app.client_manager.coriolis.endpoints
        endpoint_id = endpoints.get_endpoint_id_for_name(args.endpoint)
        edo = self.app.client_manager.coriolis.endpoint_destination_options
        obj_list = edo.list(
            endpoint_id, environment=environment, option_names=options)
        return EndpointDestinationOptionFormatter().list_objects(obj_list)

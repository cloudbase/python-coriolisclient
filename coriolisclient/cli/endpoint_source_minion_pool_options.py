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

from coriolisclient.cli import formatter
from coriolisclient.cli import utils as cli_utils


class EndpointSourceMinionPoolOptionsFormatter(formatter.EntityFormatter):

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


class ListEndpointSourceMinionPoolOptions(lister.Lister):
    """ List endpoint source minion pool options. """

    def get_parser(self, prog_name):
        parser = super(ListEndpointSourceMinionPoolOptions, self).get_parser(
            prog_name)
        parser.add_argument('endpoint', help='The endpoint\'s id')
        parser.add_argument(
            '--options', help="Names of parameters to get options for.",
            nargs='+', default=[])

        cli_utils.add_args_for_json_option_to_parser(parser, 'environment')

        return parser

    def take_action(self, args):
        environment = cli_utils.get_option_value_from_args(
            args, 'environment', error_on_no_value=False)
        options = []
        if args.options:
            options = args.options

        endpoints = self.app.client_manager.coriolis.endpoints
        endpoint_id = endpoints.get_endpoint_id_for_name(args.endpoint)
        empso = (
            self.app.client_manager.coriolis.endpoint_source_minion_pool_options)
        obj_list = empso.list(
            endpoint_id, environment=environment, option_names=options)
        return EndpointSourceMinionPoolOptionsFormatter().list_objects(obj_list)

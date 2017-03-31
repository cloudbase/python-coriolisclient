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
"""
Command-line interface sub-commands related to endpoints.
"""
import json

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient import exceptions
from coriolisclient.cli import formatter


class EndpointFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Name",
               "Type",
               "Description",
               )

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.name,
                obj.type,
                obj.description,
                )
        return data


class EndpointDetailFormatter(formatter.EntityFormatter):

    def __init__(self, show_instances_data=False):
        self.columns = [
            "id",
            "name",
            "type",
            "description",
            "connection_info",
            "last_updated",
        ]

    def _get_formatted_data(self, obj):
        data = [obj.id,
                obj.name,
                obj.type,
                obj.description,
                obj.connection_info.to_dict(),
                obj.created_at,
                obj.updated_at,
                ]

        return data


class CreateEndpoint(show.ShowOne):
    """Creates a new endpoint"""
    def get_parser(self, prog_name):
        parser = super(CreateEndpoint, self).get_parser(prog_name)

        parser.add_argument('--name', required=True,
                            help='The endpoints\'s name')
        parser.add_argument('--provider', required=True,
                            help='The provider, e.g.: '
                            'vmware_vsphere, openstack')
        parser.add_argument('--description',
                            help='A description for this endpoint')
        parser.add_argument('--connection',
                            help='JSON encoded connection data')
        parser.add_argument('--connection-secret',
                            help='The url of the Barbican secret containing '
                            'the connection info')

        return parser

    def take_action(self, args):
        if args.connection_secret and args.connection:
            raise exceptions.CoriolisException(
                "Please specify either --connection or "
                "--connection-secret, but not both")

        conn_info = None
        if args.connection_secret:
            conn_info = {"secret_ref": args.connection_secret}
        if args.connection:
            conn_info = json.loads(args.connection)

        endpoint = self.app.client_manager.coriolis.endpoints.create(
            args.name,
            args.provider,
            conn_info,
            args.description)

        return EndpointDetailFormatter().get_formatted_entity(endpoint)


class ShowEndpoint(show.ShowOne):
    """Show an endpoint"""

    def get_parser(self, prog_name):
        parser = super(ShowEndpoint, self).get_parser(prog_name)
        parser.add_argument('id', help='The endpoint\'s id')
        return parser

    def take_action(self, args):
        endpoint = self.app.client_manager.coriolis.endpoints.get(args.id)
        return EndpointDetailFormatter().get_formatted_entity(endpoint)


class DeleteEndpoint(command.Command):
    """Delete an endpoint"""

    def get_parser(self, prog_name):
        parser = super(DeleteEndpoint, self).get_parser(prog_name)
        parser.add_argument('id', help='The endpoint\'s id')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.endpoints.delete(args.id)


class ListEndpoint(lister.Lister):
    """List endpoints"""

    def get_parser(self, prog_name):
        parser = super(ListEndpoint, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        obj_list = self.app.client_manager.coriolis.endpoints.list()
        return EndpointFormatter().list_objects(obj_list)

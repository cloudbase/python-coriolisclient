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
                obj.description or "",
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
                obj.description or "",
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
        parser.add_argument('--skip-validation', dest='skip_validation',
                            action='store_true',
                            help='Whether to skip validating the connection '
                            'when creating the endpoint.')

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

        if not args.skip_validation:
            valid, message = (
                self.app.client_manager.coriolis.endpoints.validate_connection(
                    endpoint.id))
            if not valid:
                raise exceptions.EndpointConnectionValidationFailed(message)

        return EndpointDetailFormatter().get_formatted_entity(endpoint)


class UpdateEndpoint(show.ShowOne):
    """Updates an endpoint"""
    def get_parser(self, prog_name):
        parser = super(UpdateEndpoint, self).get_parser(prog_name)
        parser.add_argument('id', help='The endpoint\'s id')
        parser.add_argument('--name',
                            help='The endpoints\'s name')
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

        updated_values = {}
        if args.name is not None:
            updated_values["name"] = args.name
        if args.description is not None:
            updated_values["description"] = args.description
        if conn_info:
            updated_values["connection_info"] = conn_info

        endpoint = self.app.client_manager.coriolis.endpoints.update(
            args.id, updated_values)

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


class EndpointValidateConnection(command.Command):
    """validates an edpoint's connection"""

    def get_parser(self, prog_name):
        parser = super(EndpointValidateConnection, self).get_parser(prog_name)
        parser.add_argument('id', help='The endpoint\'s id')
        return parser

    def take_action(self, args):
        endpoints = self.app.client_manager.coriolis.endpoints
        valid, message = endpoints.validate_connection(args.id)
        if not valid:
            raise exceptions.EndpointConnectionValidationFailed(message)

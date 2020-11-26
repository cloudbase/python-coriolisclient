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

import argparse
import json

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient import exceptions
from coriolisclient.cli import formatter


def add_connection_info_args_to_parser(parser):
    """ Given an `argparse.ArgumentParser` instance, add the arguments required
    for the 'connection_info' field for both endpoint creation and updates.
    """
    conn_info_group = parser.add_mutually_exclusive_group()
    conn_info_group.add_argument('--connection',
                                 help='JSON encoded connection data')
    conn_info_group.add_argument('--connection-file',
                                 type=argparse.FileType('r'),
                                 help='Relative/full path to a file containing'
                                      ' the connection info in JSON format')
    conn_info_group.add_argument('--connection-secret',
                                 help='The url of the Barbican secret '
                                      'containing the JSON connection info')
    return parser


def get_connnection_info_from_args(args, raise_if_none=True):
    """ Returns a dict with the connection info from the arguments. """
    conn_info = None
    raw_conn_info = None
    if args.connection:
        raw_conn_info = args.connection
    elif args.connection_file:
        with args.connection_file as fin:
            raw_conn_info = fin.read()
    elif args.connection_secret:
        conn_info = {"secret_ref": args.connection_secret}

    if not conn_info and raw_conn_info:
        try:
            conn_info = json.loads(raw_conn_info)
        except ValueError as ex:
            raise ValueError(
                "Error while parsing connection info JSON: %s" % str(ex))

    if not conn_info and raise_if_none:
        raise ValueError(
            "No '--connection[-file/secret]' parameter provided.")

    return conn_info


class EndpointFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Name",
               "Type",
               "Description",
               "Mapped Region IDs")

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.name,
                obj.type,
                obj.description or "",
                obj.mapped_regions or [],
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
            "mapped_regions",
            "created_at",
            "last_updated",
        ]

    def _get_formatted_data(self, obj):
        data = [obj.id,
                obj.name,
                obj.type,
                obj.description or "",
                obj.connection_info.to_dict(),
                obj.mapped_regions or [],
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
        parser.add_argument('--skip-validation', dest='skip_validation',
                            action='store_true',
                            help='Whether to skip validating the connection '
                            'when creating the endpoint.')
        parser.add_argument('--coriolis-region', action='append',
                            dest='regions', default=[],
                            help="ID of a region the endpoint should be  "
                            "associated with. Can be supplied multiple times.")
        add_connection_info_args_to_parser(parser)

        return parser

    def take_action(self, args):
        if args.connection_secret and args.connection:
            raise exceptions.CoriolisException(
                "Please specify either --connection or "
                "--connection-secret, but not both")

        conn_info = get_connnection_info_from_args(args)
        endpoint = self.app.client_manager.coriolis.endpoints.create(
            args.name,
            args.provider,
            conn_info,
            args.description,
            regions=args.regions)

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
        parser.add_argument('--coriolis-region', action='append',
                            dest='regions', default=[],
                            help="ID of a region the endpoint should be  "
                                 "associated with. Can be supplied multiple "
                                 "times. Update will override all existing "
                                 "region associations with the one(s) provided"
                                 " if at least one region is given.")
        add_connection_info_args_to_parser(parser)
        return parser

    def take_action(self, args):
        if args.connection_secret and args.connection:
            raise exceptions.CoriolisException(
                "Please specify either --connection or "
                "--connection-secret, but not both")

        conn_info = get_connnection_info_from_args(args, raise_if_none=False)
        updated_values = {}
        if args.name is not None:
            updated_values["name"] = args.name
        if args.description is not None:
            updated_values["description"] = args.description
        if conn_info:
            updated_values["connection_info"] = conn_info
        if args.regions:
            updated_values["mapped_regions"] = args.regions

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
        client = self.app.client_manager.coriolis.endpoints
        endpoint_id = client.get_endpoint_id_for_name(args.id)
        endpoint = client.get(endpoint_id)
        return EndpointDetailFormatter().get_formatted_entity(endpoint)


class DeleteEndpoint(command.Command):
    """Delete an endpoint"""

    def get_parser(self, prog_name):
        parser = super(DeleteEndpoint, self).get_parser(prog_name)
        parser.add_argument('id', help='The endpoint\'s id')
        return parser

    def take_action(self, args):
        client = self.app.client_manager.coriolis.endpoints
        endpoint_id = client.get_endpoint_id_for_name(args.id)
        client.delete(endpoint_id)


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
        endpoint_id = endpoints.get_endpoint_id_for_name(args.id)
        valid, message = endpoints.validate_connection(endpoint_id)
        if not valid:
            raise exceptions.EndpointConnectionValidationFailed(message)

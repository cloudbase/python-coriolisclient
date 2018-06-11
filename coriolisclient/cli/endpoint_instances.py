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
import base64
import re
import sys

from cliff import lister
from cliff import show
from coriolisclient.cli import formatter


class EndpointInstanceFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Name",
               "Flavor",
               "Memory MB",
               "Cores",
               "OS Type",
               )

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.name,
                obj.flavor_name or "",
                obj.memory_mb,
                obj.num_cpu,
                obj.os_type,
                )
        return data


class InstancesDetailFormatter(formatter.EntityFormatter):

    def __init__(self, show_instances_data=False):
        self.columns = [
            "ID",
            "Name",
            "Instance name",
            "Flavor",
            "Memory MB",
            "Cores",
            "OS Type",
            "Devices"
        ]

    def _get_formatted_data(self, obj):
        data = [
            obj.id,
            obj.name,
            obj.instance_name or "",
            obj.flavor_name or "",
            obj.memory_mb,
            obj.num_cpu,
            obj.os_type,
            obj.devices
        ]

        return data


class ListEndpointInstance(lister.Lister):
    """List endpoint instances"""

    def get_parser(self, prog_name):
        parser = super(ListEndpointInstance, self).get_parser(prog_name)
        parser.add_argument('endpoint', help='The endpoint\'s id')
        parser.add_argument(
            '--marker',
            help='The id of the last instance on the previous page')
        parser.add_argument(
            '--limit', type=int, help='maximum number of instances per page')
        parser.add_argument(
            '--name',
            help='Filter results based on regular expression search')
        return parser

    def take_action(self, args):
        ei = self.app.client_manager.coriolis.endpoint_instances
        obj_list = ei.list(args.endpoint, args.marker, args.limit, args.name)
        return EndpointInstanceFormatter().list_objects(obj_list)


class ShowEndpointInstance(show.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowEndpointInstance, self).get_parser(prog_name)
        parser.add_argument(
            'endpoint', help='The endpoint ID.')
        parser.add_argument(
            'instance', help='The instance name.')
        return parser

    def take_action(self, args):
        ei = self.app.client_manager.coriolis.endpoint_instances
        if sys.version.startswith('3'):
	        byte_instance = base64.b64encode(bytes(args.instance,'utf-8'))
	        str_instance = re.sub("b'([^']*)'",r"\1",str(byte_instance))
	        obj = ei.get(args.endpoint, str_instance)
        else:
                obj = ei.get(args.endpoint, base64.b64encode(args.instance))
        return InstancesDetailFormatter().get_formatted_entity(obj)

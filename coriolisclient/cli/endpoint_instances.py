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
                obj.to_dict().get("instance_name", obj.name),
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
            "Controllers",
            "Disks",
            "Network Interfaces",
            "CDRoms",
            "Floppies",
            "Serial Ports",
        ]

    def _get_formatted_data(self, obj):
        devices = obj.devices
        data = [
            obj.id,
            obj.name,
            obj.to_dict().get("instance_name", obj.name),
            obj.flavor_name or "",
            obj.memory_mb,
            obj.num_cpu,
            obj.os_type,
            json.dumps(devices.get("controllers", []), indent=2),
            json.dumps(devices.get("disks", []), indent=2),
            json.dumps(devices.get("nics", []), indent=2),
            json.dumps(devices.get("cdroms", []), indent=2),
            json.dumps(devices.get("floppies", []), indent=2),
            json.dumps(devices.get("serial_ports", []), indent=2)
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
        parser.add_argument(
            '--env',
            help="JSON=encoded environment options for listing instances.")
        return parser

    def take_action(self, args):
        endpoints = self.app.client_manager.coriolis.endpoints
        endpoint_id = endpoints.get_endpoint_id_for_name(args.endpoint)
        ei = self.app.client_manager.coriolis.endpoint_instances
        env = None
        if args.env:
            env = json.loads(args.env)

        obj_list = ei.list(
            endpoint_id, env, args.marker, args.limit, args.name)
        return EndpointInstanceFormatter().list_objects(obj_list)


class ShowEndpointInstance(show.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ShowEndpointInstance, self).get_parser(prog_name)
        parser.add_argument(
            'endpoint', help='The endpoint ID.')
        parser.add_argument(
            'instance', help='The instance name.')
        parser.add_argument(
            '--env',
            help="JSON=encoded environment options for showing instances.")
        return parser

    def take_action(self, args):
        endpoints = self.app.client_manager.coriolis.endpoints
        endpoint_id = endpoints.get_endpoint_id_for_name(args.endpoint)
        if args.env:
            env = json.loads(args.env)
        ei = self.app.client_manager.coriolis.endpoint_instances
        obj = ei.get(
            endpoint_id, args.instance, env)
        env = None
        return InstancesDetailFormatter().get_formatted_entity(obj)

# Copyright (c) 2016 Cloudbase Solutions Srl
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
Command-line interface sub-commands related to replicas.
"""
import json
import os

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter
from coriolisclient.cli import replica_executions


class ReplicaFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Instances",
               "Last tasks execution",
               "Created",
               )

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _format_last_execution(self, obj):
        if obj.executions:
            execution = obj.executions[-1]
            return "%(id)s %(status)s" % execution.to_dict()
        return ""

    def _get_formatted_data(self, obj):
        data = (obj.id,
                "\n".join(obj.instances),
                self._format_last_execution(obj),
                obj.created_at,
                )
        return data


class ReplicaDetailFormatter(formatter.EntityFormatter):

    def __init__(self, show_instances_data=False):
        self.columns = [
            "id",
            "created",
            "last_updated",
            "instances",
            "origin_endpoint_id",
            "destination_endpoint_id",
            "target_environment",
            "executions",
        ]

        if show_instances_data:
            self.columns.append("instances-data")

    def _format_instances(self, obj):
        return os.linesep.join(sorted(obj.instances))

    def _format_target_environment(self, obj):
        if obj.target_environment is not None:
            return obj.target_environment.to_dict()
        else:
            return ""

    def _format_execution(self, execution):
        return ("%(id)s %(status)s" % execution.to_dict())

    def _format_executions(self, executions):
        return ("%(ls)s" % {"ls": os.linesep}).join(
            [self._format_execution(e) for e in
             sorted(executions, key=lambda e: e.created_at)])

    def _get_formatted_data(self, obj):
        data = [obj.id,
                obj.created_at,
                obj.updated_at,
                self._format_instances(obj),
                obj.origin_endpoint_id,
                obj.destination_endpoint_id,
                self._format_target_environment(obj),
                self._format_executions(obj.executions),
                ]

        if "instances-data" in self.columns:
            data.append(obj.info)

        return data


class CreateReplica(show.ShowOne):
    """Create a new replica"""
    def get_parser(self, prog_name):
        parser = super(CreateReplica, self).get_parser(prog_name)
        parser.add_argument('--origin-endpoint', required=True,
                            help='The origin endpoint id')
        parser.add_argument('--destination-endpoint', required=True,
                            help='The destination endpoint id')
        parser.add_argument('--target-environment',
                            help='JSON encoded data related to the '
                            'destination\'s target environment')
        parser.add_argument('--instance', action='append', required=True,
                            dest="instances",
                            help='An instances to be migrated, can be '
                            'specified multiple times')
        return parser

    def take_action(self, args):
        target_environment = None
        if args.target_environment:
            target_environment = json.loads(args.target_environment)

        replica = self.app.client_manager.coriolis.replicas.create(
            args.origin_endpoint,
            args.destination_endpoint,
            target_environment,
            args.instances)

        return ReplicaDetailFormatter().get_formatted_entity(replica)


class ShowReplica(show.ShowOne):
    """Show a replica"""

    def get_parser(self, prog_name):
        parser = super(ShowReplica, self).get_parser(prog_name)
        parser.add_argument('id', help='The replica\'s id')
        parser.add_argument('--show-instances-data', action='store_true',
                            help='Includes the instances data used for tasks '
                            'execution, this is useful for troubleshooting',
                            default=False)
        return parser

    def take_action(self, args):
        replica = self.app.client_manager.coriolis.replicas.get(args.id)
        return ReplicaDetailFormatter(
            args.show_instances_data).get_formatted_entity(replica)


class DeleteReplica(command.Command):
    """Delete a replica"""

    def get_parser(self, prog_name):
        parser = super(DeleteReplica, self).get_parser(prog_name)
        parser.add_argument('id', help='The replica\'s id')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.replicas.delete(args.id)


class DeleteReplicaDisks(show.ShowOne):
    """Delete replica target disks"""

    def get_parser(self, prog_name):
        parser = super(DeleteReplicaDisks, self).get_parser(prog_name)
        parser.add_argument('id', help='The replica\'s id')
        return parser

    def take_action(self, args):
        execution = self.app.client_manager.coriolis.replicas.delete_disks(
            args.id)
        return replica_executions.ReplicaExecutionDetailFormatter(
        ).get_formatted_entity(execution)


class ListReplica(lister.Lister):
    """List replicas"""

    def get_parser(self, prog_name):
        parser = super(ListReplica, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        obj_list = self.app.client_manager.coriolis.replicas.list()
        return ReplicaFormatter().list_objects(obj_list)

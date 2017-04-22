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
import os

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter


class ReplicaExecutionFormatter(formatter.EntityFormatter):

    columns = ("Replica ID",
               "ID",
               "Status",
               "Created",
               )

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _get_formatted_data(self, obj):
        data = (obj.action_id,
                obj.id,
                obj.status,
                obj.created_at,
                )
        return data


class ReplicaExecutionDetailFormatter(formatter.EntityFormatter):

    columns = ("id",
               "replica_id",
               "status",
               "created",
               "last_updated",
               "instances",
               "tasks",
               )

    def _format_instances(self, obj):
        return os.linesep.join(sorted(set([t.instance for t in obj.tasks])))

    def _format_progress_update(self, progress_update):
        return (
            "%(created_at)s %(message)s" % progress_update)

    def _format_progress_updates(self, task_dict):
        return ("%(ls)s" % {"ls": os.linesep}).join(
            [self._format_progress_update(p) for p in
             sorted(task_dict.get("progress_updates", []),
                    key=lambda p: (p["current_step"], p["created_at"]))])

    def _format_task(self, task):
        d = task.to_dict()
        d["depends_on"] = ", ".join(d.get("depends_on") or [])

        progress_updates_format = "progress_updates:"
        progress_updates = self._format_progress_updates(d)
        if progress_updates:
            progress_updates_format += os.linesep
            progress_updates_format += progress_updates

        return os.linesep.join(
            ["%s: %s" % (k, d.get(k) or "") for k in
                ['id',
                 'task_type',
                 'instance',
                 'status',
                 'depends_on',
                 'exception_details']] +
            [progress_updates_format])

    def _format_tasks(self, obj):
        return ("%(ls)s%(ls)s" % {"ls": os.linesep}).join(
            [self._format_task(t) for t in obj.tasks])

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.action_id,
                obj.status,
                obj.created_at,
                obj.updated_at,
                self._format_instances(obj),
                self._format_tasks(obj),
                )
        return data


class CreateReplicaExecution(show.ShowOne):
    """Start a replica execution"""
    def get_parser(self, prog_name):
        parser = super(CreateReplicaExecution, self).get_parser(prog_name)
        parser.add_argument('replica',
                            help='The ID of the replica to execute')
        parser.add_argument('--shutdown-instances',
                            help='Shutdown instances before executing the '
                            'replica', action='store_true',
                            default=False)
        return parser

    def take_action(self, args):
        execution = self.app.client_manager.coriolis.replica_executions.create(
            args.replica, args.shutdown_instances)

        return ReplicaExecutionDetailFormatter().get_formatted_entity(
            execution)


class ShowReplicaExecution(show.ShowOne):
    """Show a replica execution"""

    def get_parser(self, prog_name):
        parser = super(ShowReplicaExecution, self).get_parser(prog_name)
        parser.add_argument('replica', help='The replica\'s id')
        parser.add_argument('id', help='The replica execution\'s id')
        return parser

    def take_action(self, args):
        execution = self.app.client_manager.coriolis.replica_executions.get(
            args.replica, args.id)
        return ReplicaExecutionDetailFormatter().get_formatted_entity(
            execution)


class CancelReplicaExecution(command.Command):
    """Cancel a replica execution"""

    def get_parser(self, prog_name):
        parser = super(CancelReplicaExecution, self).get_parser(prog_name)
        parser.add_argument('replica', help='The replica\'s id')
        parser.add_argument('id', help='The replica execution\'s id')
        parser.add_argument('--force',
                            help='Perform a forced termination of running '
                            'tasks', action='store_true',
                            default=False)
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.replica_executions.cancel(
            args.replica, args.id, args.force)


class DeleteReplicaExecution(command.Command):
    """Delete a replica execution"""

    def get_parser(self, prog_name):
        parser = super(DeleteReplicaExecution, self).get_parser(prog_name)
        parser.add_argument('replica', help='The replica\'s id')
        parser.add_argument('id', help='The replica execution\'s id')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.replica_executions.delete(
            args.replica, args.id)


class ListReplicaExecution(lister.Lister):
    """List replica executions"""

    def get_parser(self, prog_name):
        parser = super(ListReplicaExecution, self).get_parser(prog_name)
        parser.add_argument('replica', help='The replica\'s id')
        return parser

    def take_action(self, args):
        obj_list = self.app.client_manager.coriolis.replica_executions.list(
            args.replica)
        return ReplicaExecutionFormatter().list_objects(obj_list)

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
Command-line interface sub-commands related to migrations.
"""
import json
import os

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter


class MigrationFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Status",
               "Instances",
               "Created",
               )

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.status,
                "\n".join(obj.instances),
                obj.created_at,
                )
        return data


class MigrationDetailFormatter(formatter.EntityFormatter):

    def __init__(self, show_instances_data=False):
        self.columns = [
            "id",
            "status",
            "created",
            "last_updated",
            "instances",
            "origin_endpoint_id",
            "destination_endpoint_id",
            "destination_environment",
            "tasks",
        ]

        if show_instances_data:
            self.columns.append("instances_data")

    def _format_instances(self, obj):
        return os.linesep.join(sorted(obj.instances))

    def _format_destination_environment(self, obj):
        if obj.destination_environment is not None:
            return obj.destination_environment.to_dict()
        else:
            return ""

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
        data = [obj.id,
                obj.status,
                obj.created_at,
                obj.updated_at,
                self._format_instances(obj),
                obj.origin_endpoint_id,
                obj.destination_endpoint_id,
                self._format_destination_environment(obj),
                self._format_tasks(obj),
                ]

        if "instances-data" in self.columns:
            data.append(obj.info)

        return data


class MigrationCleanupResultFormatter(formatter.EntityFormatter):

    columns = ("Instance Name",
               "Cleanup Successful",
               "Error Message")

    def _get_formatted_data(self, obj):
        data = (obj["instance_name"],
                obj["success"],
                obj["error_message"])
        return data


class CreateMigration(show.ShowOne):
    """Start a new migration"""
    def get_parser(self, prog_name):
        parser = super(CreateMigration, self).get_parser(prog_name)
        parser.add_argument('--origin-endpoint', required=True,
                            help='The origin endpoint id')
        parser.add_argument('--destination-endpoint', required=True,
                            help='The destination endpoint id')
        parser.add_argument('--destination-environment',
                            help='JSON encoded data related to the '
                            'destination\'s environment')
        parser.add_argument('--instance', action='append', required=True,
                            dest="instances",
                            help='An instances to be migrated, can be '
                            'specified multiple times')
        parser.add_argument('--skip-os-morphing',
                            help='Skip the OS morphing process',
                            action='store_true',
                            default=False)
        return parser

    def take_action(self, args):
        destination_environment = None
        if args.destination_environment:
            destination_environment = json.loads(args.destination_environment)

        migration = self.app.client_manager.coriolis.migrations.create(
            args.origin_endpoint,
            args.destination_endpoint,
            destination_environment,
            args.instances,
            args.skip_os_morphing)

        return MigrationDetailFormatter().get_formatted_entity(migration)


class CreateMigrationFromReplica(show.ShowOne):
    """Start a new migration from an existing replica"""
    def get_parser(self, prog_name):
        parser = super(CreateMigrationFromReplica, self).get_parser(prog_name)
        parser.add_argument('replica',
                            help='The ID of the replica to migrate')
        parser.add_argument('--force',
                            help='Force the migration in case of a replica '
                            'with failed executions', action='store_true',
                            default=False)
        parser.add_argument('--dont-clone-disks',
                            help='Retain the replica disks by cloning them',
                            action='store_false', dest="clone_disks",
                            default=True)
        parser.add_argument('--skip-os-morphing',
                            help='Skip the OS morphing process',
                            action='store_true',
                            default=False)
        return parser

    def take_action(self, args):
        m = self.app.client_manager.coriolis.migrations
        migration = m.create_from_replica(
            args.replica,
            args.clone_disks,
            args.force,
            args.skip_os_morphing)

        return MigrationDetailFormatter().get_formatted_entity(migration)


class ShowMigration(show.ShowOne):
    """Show a migration"""

    def get_parser(self, prog_name):
        parser = super(ShowMigration, self).get_parser(prog_name)
        parser.add_argument('id', help='The migration\'s id')
        parser.add_argument('--show-instances-data', action='store_true',
                            help='Includes the instances data used for tasks '
                            'execution, this is useful for troubleshooting',
                            default=False)
        return parser

    def take_action(self, args):
        migration = self.app.client_manager.coriolis.migrations.get(args.id)
        return MigrationDetailFormatter(
            args.show_instances_data).get_formatted_entity(migration)


class CancelMigration(command.Command):
    """Cancel a migration"""

    def get_parser(self, prog_name):
        parser = super(CancelMigration, self).get_parser(prog_name)
        parser.add_argument('id', help='The migration\'s id')
        parser.add_argument('--force',
                            help='Perform a forced termination of running '
                            'tasks', action='store_true',
                            default=False)
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.migrations.cancel(args.id, args.force)


class CleanupMigrationSourceResources(lister.Lister):
    """ Cleanup migration source resources. """

    def get_parser(self, prog_name):
        parser = super(CleanupMigrationSourceResources, self).get_parser(
            prog_name)
        parser.add_argument('id', help='The migration\'s id')
        parser.add_argument('--cleanup-options',
                            required=True,
                            help='JSON Cleanup Options specific to the '
                                 'source provider')
        return parser

    def take_action(self, args):
        migrations_api = self.app.client_manager.coriolis.migrations
        cleanup_opts = json.loads(args.cleanup_options)

        results = migrations_api.cleanup_source_vm_resources(
            args.id, cleanup_opts).json().get(
                "cleanup-source-vm-resources")

        return MigrationCleanupResultFormatter().list_objects(results)


class DeleteMigration(command.Command):
    """Delete a migration"""

    def get_parser(self, prog_name):
        parser = super(DeleteMigration, self).get_parser(prog_name)
        parser.add_argument('id', help='The migration\'s id')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.migrations.delete(args.id)


class ListMigration(lister.Lister):
    """List migrations"""

    def get_parser(self, prog_name):
        parser = super(ListMigration, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        obj_list = self.app.client_manager.coriolis.migrations.list()
        return MigrationFormatter().list_objects(obj_list)

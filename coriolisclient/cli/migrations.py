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

from coriolisclient import exceptions
from coriolisclient.cli import formatter


class MigrationFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Status",
               "Created",
               )

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.status,
                obj.created_at,
                )
        return data


class MigrationDetailFormatter(formatter.EntityFormatter):

    columns = ("id",
               "status",
               "created",
               "last_updated",
               "instances",
               "origin-provider",
               "origin-connection",
               "destination-provider",
               "destination-connection",
               "tasks",
               )

    def _format_instances(self, obj):
        return os.linesep.join(sorted(set([t.instance for t in obj.tasks])))

    def _format_conn_info(self, endpoint):
        return endpoint.to_dict().get("connection_info") or ""

    def _format_progress_update(self, progress_update):
        return (
            "%(created_at)s %(message)s" % progress_update)

    def _format_progress_updates(self, task_dict):
        return ("%(ls)s" % {"ls": os.linesep}).join(
            [self._format_progress_update(p) for p in
             sorted(task_dict.get("progress_updates", []),
                    key=lambda p: p["created_at"])])

    def _format_task(self, task):
        d = task.to_dict()

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
            [self._format_task(t) for t in
             sorted(obj.tasks, key=lambda t: t.task_type)])

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.status,
                obj.created_at,
                obj.updated_at,
                self._format_instances(obj),
                obj.origin.type,
                self._format_conn_info(obj.origin),
                obj.destination.type,
                self._format_conn_info(obj.destination),
                self._format_tasks(obj),
                )
        return data


class CreateMigration(show.ShowOne):
    """Starts a new migration."""
    def get_parser(self, prog_name):
        parser = super(CreateMigration, self).get_parser(prog_name)
        parser.add_argument('--origin-provider', required=True,
                            help='The origin provider, e.g.: '
                            'vmware_vsphere, openstack')
        parser.add_argument('--origin-connection',
                            help='JSON encoded origin connection data')
        parser.add_argument('--origin-connection-secret',
                            help='The url of the Barbican secret containing '
                            'the origin connection info')
        parser.add_argument('--destination-provider', required=True,
                            help='The destination provider, e.g.: '
                            'vmware_vsphere, openstack')
        parser.add_argument('--destination-connection',
                            help='JSON encoded destination connection data')
        parser.add_argument('--destination-connection-secret',
                            help='The url of the Barbican secret containing '
                            'the destination connection info')
        parser.add_argument('--target-environment',
                            help='JSON encoded data related to the '
                            'destination\'s target environment')
        parser.add_argument('--instance', action='append', required=True,
                            dest="instances",
                            help='An instances to be migrated, can be '
                            'specified multiple times')

        return parser

    def take_action(self, args):
        if args.origin_connection_secret and args.origin_connection:
            raise exceptions.CoriolisException(
                "Please specify either --origin-connection or "
                "--origin-connection-secret, but not both")

        if args.destination_connection_secret and args.destination_connection:
            raise exceptions.CoriolisException(
                "Please specify either --destination-connection or "
                "--destination-connection-secret, but not both")

        origin_conn_info = None
        if args.origin_connection_secret:
            origin_conn_info = {"secret_ref": args.origin_connection_secret}
        if args.origin_connection:
            origin_conn_info = json.loads(args.origin_connection)

        dest_conn_info = None
        if args.destination_connection_secret:
            dest_conn_info = {"secret_ref": args.destination_connection_secret}
        if args.destination_connection:
            dest_conn_info = json.loads(args.destination_connection)

        target_environment = None
        if args.target_environment:
            target_environment = json.loads(args.target_environment)

        migration = self.app.client_manager.coriolis.migrations.create(
            args.origin_provider,
            origin_conn_info,
            args.destination_provider,
            dest_conn_info,
            target_environment,
            args.instances)

        return MigrationDetailFormatter().get_formatted_entity(migration)


class ShowMigration(show.ShowOne):
    """Retrieve a migration by providing its id."""

    def get_parser(self, prog_name):
        parser = super(ShowMigration, self).get_parser(prog_name)
        parser.add_argument('id', help='The migration\'s id')
        return parser

    def take_action(self, args):
        migration = self.app.client_manager.coriolis.migrations.get(args.id)
        return MigrationDetailFormatter().get_formatted_entity(migration)


class CancelMigration(command.Command):
    """Cancels a migration by providing its id."""

    def get_parser(self, prog_name):
        parser = super(CancelMigration, self).get_parser(prog_name)
        parser.add_argument('id', help='The migration\'s id')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.migrations.cancel(args.id)


class DeleteMigration(command.Command):
    """Delete a migration by providing its id."""

    def get_parser(self, prog_name):
        parser = super(DeleteMigration, self).get_parser(prog_name)
        parser.add_argument('id', help='The migration\'s id')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.migrations.delete(args.id)


class ListMigration(lister.Lister):
    """List migrations."""

    def get_parser(self, prog_name):
        parser = super(ListMigration, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        obj_list = self.app.client_manager.coriolis.migrations.list()
        return MigrationFormatter().list_objects(obj_list)

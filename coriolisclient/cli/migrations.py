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

import os

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter
from coriolisclient.cli import utils as cli_utils


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
            "reservation_id",
            "instances",
            "origin_endpoint_id",
            "origin_minion_pool_id",
            "destination_endpoint_id",
            "destination_minion_pool_id",
            "instance_osmorphing_minion_pool_mappings",
            "replication_count",
            "shutdown_instances",
            "destination_environment",
            "source_environment",
            "network_map",
            "disk_storage_mappings",
            "storage_backend_mappings",
            "default_storage_backend",
            "user_scripts",
            "tasks",
            "transfer_result"
        ]

        if show_instances_data:
            self.columns.append("instances_data")

    def _format_instances(self, obj):
        return os.linesep.join(sorted(obj.instances))

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
        storage_mappings = obj.to_dict().get("storage_mappings", {})
        default_storage, backend_mappings, disk_mappings = (
            cli_utils.parse_storage_mappings(storage_mappings))
        data = [obj.id,
                obj.status,
                obj.created_at,
                obj.updated_at,
                obj.reservation_id,
                self._format_instances(obj),
                obj.origin_endpoint_id,
                obj.origin_minion_pool_id,
                obj.destination_endpoint_id,
                obj.destination_minion_pool_id,
                cli_utils.format_json_for_object_property(
                    obj, 'instance_osmorphing_minion_pool_mappings'),
                getattr(obj, 'replication_count', None),
                getattr(obj, 'shutdown_instances', False),
                cli_utils.format_json_for_object_property(
                    obj, prop_name="destination_environment"),
                cli_utils.format_json_for_object_property(
                    obj, 'source_environment'),
                cli_utils.format_json_for_object_property(obj, 'network_map'),
                cli_utils.format_mapping(disk_mappings),
                cli_utils.format_mapping(backend_mappings),
                default_storage,
                cli_utils.format_json_for_object_property(obj, 'user_scripts'),
                self._format_tasks(obj),
                cli_utils.format_json_for_object_property(
                    obj, 'transfer_result')
                ]

        if "instances_data" in self.columns:
            data.append(obj.info)

        return data


class CreateMigration(show.ShowOne):
    """Start a new migration"""
    def get_parser(self, prog_name):
        parser = super(CreateMigration, self).get_parser(prog_name)
        parser.add_argument('--origin-endpoint', required=True,
                            help='The origin endpoint id')
        parser.add_argument('--destination-endpoint', required=True,
                            help='The destination endpoint id')
        parser.add_argument('--instance', action='append', required=True,
                            dest="instances", metavar="INSTANCE_IDENTIFIER",
                            help='The identifier of a source instance to be '
                                 'migrated. Can be specified multiple times')
        parser.add_argument('--user-script-global', action='append',
                            required=False,
                            dest="global_scripts",
                            help='A script that will run for a particular '
                            'os_type. This option can be used multiple '
                            'times. Use: linux=/path/to/script.sh or '
                            'windows=/path/to/script.ps1')
        parser.add_argument('--user-script-instance', action='append',
                            required=False,
                            dest="instance_scripts",
                            help='A script that will run for a particular '
                            'instance specified by the --instance option. '
                            'This option can be used multiple times. '
                            'Use: "instance_name"=/path/to/script.sh.'
                            ' This option overwrites any OS specific script '
                            'specified in --user-script-global for this '
                            'instance')
        parser.add_argument('--skip-os-morphing',
                            help='Skip the OS morphing process',
                            action='store_true',
                            default=False)
        parser.add_argument('--replication-count',
                            type=int,
                            help='Number of times to perform a replica sync '
                                 'before deploying the migrated instance.')
        parser.add_argument('--shutdown-instances',
                            action='store_true',
                            help='Whether or not to shut down the instance on '
                                 'the source platform before performing the '
                                 'final Replica sync')

        cli_utils.add_args_for_json_option_to_parser(
            parser, 'destination-environment')
        cli_utils.add_args_for_json_option_to_parser(parser, 'network-map')
        cli_utils.add_args_for_json_option_to_parser(
            parser, 'source-environment')
        cli_utils.add_storage_mappings_arguments_to_parser(parser)
        cli_utils.add_minion_pool_args_to_parser(
            parser, include_origin_pool_arg=True,
            include_destination_pool_arg=True,
            include_osmorphing_pool_mappings_arg=True)

        return parser

    def take_action(self, args):
        destination_environment = cli_utils.get_option_value_from_args(
            args, 'destination-environment')
        source_environment = cli_utils.get_option_value_from_args(
            args, 'source-environment')
        network_map = cli_utils.get_option_value_from_args(
            args, 'network-map')
        storage_mappings = cli_utils.get_storage_mappings_dict_from_args(args)
        endpoints = self.app.client_manager.coriolis.endpoints
        origin_endpoint_id = endpoints.get_endpoint_id_for_name(
            args.origin_endpoint)
        destination_endpoint_id = endpoints.get_endpoint_id_for_name(
            args.destination_endpoint)
        user_scripts = cli_utils.compose_user_scripts(
            args.global_scripts, args.instance_scripts)
        instance_osmorphing_minion_pool_mappings = None
        if args.instance_osmorphing_minion_pool_mappings:
            instance_osmorphing_minion_pool_mappings = {
                mp['instance_id']: mp['pool_id']
                for mp in args.instance_osmorphing_minion_pool_mappings}

        migration = self.app.client_manager.coriolis.migrations.create(
            origin_endpoint_id,
            destination_endpoint_id,
            source_environment,
            destination_environment,
            args.instances,
            network_map=network_map,
            storage_mappings=storage_mappings,
            skip_os_morphing=args.skip_os_morphing,
            replication_count=args.replication_count,
            shutdown_instances=args.shutdown_instances,
            origin_minion_pool_id=args.origin_minion_pool_id,
            destination_minion_pool_id=args.destination_minion_pool_id,
            instance_osmorphing_minion_pool_mappings=(
                instance_osmorphing_minion_pool_mappings),
            user_scripts=user_scripts)

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
        parser.add_argument('--user-script-global', action='append',
                            required=False,
                            dest="global_scripts",
                            help='A script that will run for a particular '
                            'os_type. This option can be used multiple '
                            'times. Use: linux=/path/to/script.sh or '
                            'windows=/path/to/script.ps1')
        parser.add_argument('--user-script-instance', action='append',
                            required=False,
                            dest="instance_scripts",
                            help='A script that will run for a particular '
                            'instance specified by the --instance option. '
                            'This option can be used multiple times. '
                            'Use: "instance_name"=/path/to/script.sh.'
                            ' This option overwrites any OS specific script '
                            'specified in --user-script-global for this '
                            'instance')
        cli_utils.add_minion_pool_args_to_parser(
            parser, include_origin_pool_arg=False,
            include_destination_pool_arg=False,
            include_osmorphing_pool_mappings_arg=True)

        return parser

    def take_action(self, args):
        m = self.app.client_manager.coriolis.migrations
        user_scripts = cli_utils.compose_user_scripts(
            args.global_scripts, args.instance_scripts)
        instance_osmorphing_minion_pool_mappings = None
        if args.instance_osmorphing_minion_pool_mappings:
            instance_osmorphing_minion_pool_mappings = {
                mp['instance_id']: mp['pool_id']
                for mp in args.instance_osmorphing_minion_pool_mappings}

        migration = m.create_from_replica(
            args.replica,
            args.clone_disks,
            args.force,
            args.skip_os_morphing,
            user_scripts=user_scripts,
            instance_osmorphing_minion_pool_mappings=(
                instance_osmorphing_minion_pool_mappings))

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

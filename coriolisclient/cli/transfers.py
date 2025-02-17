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
Command-line interface sub-commands related to transfers.
"""

import os

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter
from coriolisclient.cli import transfer_executions
from coriolisclient.cli import utils as cli_utils

TRANSFER_SCENARIO_REPLICA = "replica"
TRANSFER_SCENARIO_LIVE_MIGRATION = "live_migration"


def _add_default_deployment_args_to_parser(parser):
    cd_group = parser.add_mutually_exclusive_group()
    cd_group.add_argument('--clone-disks',
                          help='Retain the transfer disks by cloning them '
                               'when launching deployment',
                          action='store_true', dest="clone_disks",
                          default=None)
    cd_group.add_argument('--dont-clone-disks',
                          help="Deploy directly on transfer disks, without "
                               "cloning them.",
                          action="store_false", dest="clone_disks",
                          default=None)

    osm_group = parser.add_mutually_exclusive_group()
    osm_group.add_argument('--os-morphing',
                           help="Include the OSMorphing process on the "
                                "deployments of this transfer.",
                           action="store_false", dest="skip_os_morphing",
                           default=None)
    osm_group.add_argument('--skip-os-morphing',
                           help='Skip the OS morphing process on the '
                                'deployments of this transfer',
                           action='store_true', default=None,
                           dest="skip_os_morphing")


class TransferFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Scenario",
               "Instances",
               "Notes",
               "Last Execution Status",
               "Created",
               )

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _format_last_execution(self, obj):
        if obj.executions:
            execution = sorted(obj.executions, key=lambda e: e.created_at)[-1]
            return "%(id)s %(status)s" % execution.to_dict()
        return ""

    def _get_formatted_data(self, obj):
        data = (obj.id,
                getattr(obj, "scenario", "replica"),
                "\n".join(obj.instances),
                obj.notes,
                obj.last_execution_status,
                obj.created_at,
                )
        return data


class TransferDetailFormatter(formatter.EntityFormatter):

    def __init__(self, show_instances_data=False):
        self.columns = [
            "id",
            "created",
            "last_updated",
            "scenario_type",
            "reservation_id",
            "instances",
            "notes",
            "origin_endpoint_id",
            "origin_minion_pool_id",
            "destination_endpoint_id",
            "destination_minion_pool_id",
            "instance_osmorphing_minion_pool_mappings",
            "destination_environment",
            "source_environment",
            "network_map",
            "disk_storage_mappings",
            "storage_backend_mappings",
            "default_storage_backend",
            "user_scripts",
            "clone_disks",
            "skip_os_morphing",
            "executions",
        ]

        if show_instances_data:
            self.columns.append("instances-data")

    def _format_instances(self, obj):
        return os.linesep.join(sorted(obj.instances))

    def _format_execution(self, execution):
        return ("%(id)s %(status)s" % execution.to_dict())

    def _format_executions(self, executions):
        return ("%(ls)s" % {"ls": os.linesep}).join(
            [self._format_execution(e) for e in
             sorted(executions, key=lambda e: e.created_at)])

    def _get_formatted_data(self, obj):
        storage_mappings = obj.to_dict().get("storage_mappings", {})
        default_storage, backend_mappings, disk_mappings = (
            cli_utils.parse_storage_mappings(storage_mappings))
        data = [obj.id,
                obj.created_at,
                obj.updated_at,
                getattr(obj, "scenario", ""),
                obj.reservation_id,
                self._format_instances(obj),
                obj.notes,
                obj.origin_endpoint_id,
                obj.origin_minion_pool_id,
                obj.destination_endpoint_id,
                obj.destination_minion_pool_id,
                cli_utils.format_json_for_object_property(
                    obj, 'instance_osmorphing_minion_pool_mappings'),
                cli_utils.format_json_for_object_property(
                    obj, prop_name="destination_environment"),
                cli_utils.format_json_for_object_property(
                    obj, 'source_environment'),
                cli_utils.format_json_for_object_property(
                    obj, 'network_map'),
                cli_utils.format_mapping(disk_mappings),
                cli_utils.format_mapping(backend_mappings),
                default_storage,
                cli_utils.format_json_for_object_property(obj, 'user_scripts'),
                obj.clone_disks,
                obj.skip_os_morphing,
                self._format_executions(obj.executions)]

        if "instances-data" in self.columns:
            data.append(obj.info)

        return data


class CreateTransfer(show.ShowOne):
    """Create a new transfer"""
    def get_parser(self, prog_name):
        parser = super(CreateTransfer, self).get_parser(prog_name)
        parser.add_argument('--origin-endpoint', required=True,
                            help='The origin endpoint id')
        parser.add_argument('--destination-endpoint', required=True,
                            help='The destination endpoint id')
        parser.add_argument('--instance', action='append', required=True,
                            dest="instances", metavar="INSTANCE_IDENTIFIER",
                            help='The identifier of a source instance to be '
                                 'transferred. Can be specified multiple '
                                 'times')
        parser.add_argument('--scenario',
                            dest="scenario", metavar="SCENARIO",
                            choices=[
                                TRANSFER_SCENARIO_REPLICA,
                                TRANSFER_SCENARIO_LIVE_MIGRATION],
                            default=TRANSFER_SCENARIO_REPLICA,
                            help='The type of scenario to use when creating '
                                 'the Transfer. "replica" will create a '
                                 'monthly-billed Replica which can be '
                                 'executed and deployed as many times as '
                                 'desired, while "live_migration" will '
                                 'create a Transfer which can be synced '
                                 'as many times as needed but only '
                                 'deployed once.')
        parser.add_argument('--notes', dest='notes',
                            help='Notes about the transfer')
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

        cli_utils.add_args_for_json_option_to_parser(
            parser, 'destination-environment')
        cli_utils.add_args_for_json_option_to_parser(parser, 'network-map')
        cli_utils.add_args_for_json_option_to_parser(
            parser, 'source-environment')
        cli_utils.add_minion_pool_args_to_parser(
            parser, include_origin_pool_arg=True,
            include_destination_pool_arg=True,
            include_osmorphing_pool_mappings_arg=True)

        cli_utils.add_storage_mappings_arguments_to_parser(parser)
        _add_default_deployment_args_to_parser(parser)

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
        instance_osmorphing_minion_pool_mappings = None
        if args.instance_osmorphing_minion_pool_mappings:
            instance_osmorphing_minion_pool_mappings = {
                mp['instance_id']: mp['pool_id']
                for mp in args.instance_osmorphing_minion_pool_mappings}
        user_scripts = cli_utils.compose_user_scripts(
            args.global_scripts, args.instance_scripts)

        transfer = self.app.client_manager.coriolis.transfers.create(
            origin_endpoint_id,
            destination_endpoint_id,
            source_environment,
            destination_environment,
            args.instances,
            args.scenario,
            network_map=network_map,
            notes=args.notes,
            storage_mappings=storage_mappings,
            origin_minion_pool_id=args.origin_minion_pool_id,
            destination_minion_pool_id=args.destination_minion_pool_id,
            instance_osmorphing_minion_pool_mappings=(
                instance_osmorphing_minion_pool_mappings),
            user_scripts=user_scripts,
            clone_disks=args.clone_disks,
            skip_os_morphing=args.skip_os_morphing)

        return TransferDetailFormatter().get_formatted_entity(transfer)


class ShowTransfer(show.ShowOne):
    """Show a transfer"""

    def get_parser(self, prog_name):
        parser = super(ShowTransfer, self).get_parser(prog_name)
        parser.add_argument('id', help='The transfer\'s id')
        parser.add_argument('--show-instances-data', action='store_true',
                            help='Includes the instances data used for tasks '
                            'execution, this is useful for troubleshooting',
                            default=False)
        return parser

    def take_action(self, args):
        transfer = self.app.client_manager.coriolis.transfers.get(args.id)
        return TransferDetailFormatter(
            args.show_instances_data).get_formatted_entity(transfer)


class DeleteTransfer(command.Command):
    """Delete a transfer"""

    def get_parser(self, prog_name):
        parser = super(DeleteTransfer, self).get_parser(prog_name)
        parser.add_argument('id', help='The transfer\'s id')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.transfers.delete(args.id)


class DeleteTransferDisks(show.ShowOne):
    """Delete transfer target disks"""

    def get_parser(self, prog_name):
        parser = super(DeleteTransferDisks, self).get_parser(prog_name)
        parser.add_argument('id', help='The transfer\'s id')
        return parser

    def take_action(self, args):
        execution = self.app.client_manager.coriolis.transfers.delete_disks(
            args.id)
        return transfer_executions.TransferExecutionDetailFormatter(
        ).get_formatted_entity(execution)


class ListTransfer(lister.Lister):
    """List transfers"""

    def get_parser(self, prog_name):
        parser = super(ListTransfer, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        obj_list = self.app.client_manager.coriolis.transfers.list()
        return TransferFormatter().list_objects(obj_list)


class UpdateTransfer(show.ShowOne):
    """Create a new transfer"""
    def get_parser(self, prog_name):
        parser = super(UpdateTransfer, self).get_parser(prog_name)
        parser.add_argument('id', help='The transfer\'s id')
        parser.add_argument('--notes', dest='notes',
                            help='Notes about the transfer.')
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
        _add_default_deployment_args_to_parser(parser)

        return parser

    def take_action(self, args):
        destination_environment = cli_utils.get_option_value_from_args(
            args, 'destination-environment', error_on_no_value=False)
        source_environment = cli_utils.get_option_value_from_args(
            args, 'source-environment', error_on_no_value=False)
        network_map = cli_utils.get_option_value_from_args(
            args, 'network-map', error_on_no_value=False)
        storage_mappings = cli_utils.get_storage_mappings_dict_from_args(args)
        user_scripts = cli_utils.compose_user_scripts(
            args.global_scripts, args.instance_scripts)

        updated_properties = {}
        if destination_environment:
            updated_properties[
                'destination_environment'] = destination_environment
        if source_environment:
            updated_properties['source_environment'] = source_environment
        if storage_mappings:
            updated_properties['storage_mappings'] = storage_mappings
        if network_map:
            updated_properties['network_map'] = network_map
        if args.notes:
            updated_properties['notes'] = args.notes
        if args.origin_minion_pool_id is not None:
            # NOTE: allow for unsetting by specifying an empty string:
            updated_properties['origin_minion_pool_id'] = (
                args.origin_minion_pool_id or None)
        if args.destination_minion_pool_id is not None:
            # NOTE: allow for unsetting by specifying an empty string:
            updated_properties['destination_minion_pool_id'] = (
                args.destination_minion_pool_id or None)
        if args.instance_osmorphing_minion_pool_mappings:
            instance_osmorphing_minion_pool_mappings = {
                mp['instance_id']: mp['pool_id']
                for mp in args.instance_osmorphing_minion_pool_mappings}
            updated_properties['instance_osmorphing_minion_pool_mappings'] = (
                instance_osmorphing_minion_pool_mappings)
        if user_scripts:
            updated_properties['user_scripts'] = user_scripts
        if args.clone_disks is not None:
            updated_properties['clone_disks'] = args.clone_disks
        if args.skip_os_morphing is not None:
            updated_properties['skip_os_morphing'] = args.skip_os_morphing

        if not updated_properties:
            raise ValueError(
                "No options provided for update. Please run `coriolis help "
                "transfer update` for details on accepted parameters.")

        execution = self.app.client_manager.coriolis.transfers.update(
            args.id, updated_properties)

        return transfer_executions.TransferExecutionDetailFormatter(
        ).get_formatted_entity(execution)

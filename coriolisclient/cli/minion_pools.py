# Copyright (c) 2020 Cloudbase Solutions Srl
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
Command-line interface sub-commands related to minion_pools.
"""

import os

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter
from coriolisclient.cli import utils as cli_utils


class MinionPoolFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Pool Name",
               "Endpoint",
               "Pool Platform",
               "OS Type",
               "Notes",
               "Pool Status",
               "Minions (Min - Max)")

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.name,
                obj.endpoint_id,
                obj.platform,
                obj.os_type,
                obj.notes,
                obj.status,
                "%s - %s" % (
                    obj.minimum_minions, obj.maximum_minions))

        return data


class MinionPoolDetailFormatter(formatter.EntityFormatter):

    columns = ("ID",
               "Pool Name",
               "Endpoint",
               "Pool Platform",
               "OS Type",
               "Pool Status",
               "Notes",
               "Created At",
               "Updated At",
               "Maintenance Trust ID",
               "Minimum Minions",
               "Maximum Minions",
               "Minion Max Idle Time",
               "Minion Retention Strategy",
               "Environment Options",
               "Shared Resources",
               "Events",
               "Progress Updates",
               "Minion Machines")

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _format_pool_event(self, event):
        return (
            "%(level)s %(created_at)s %(message)s" % event)

    def _format_pool_events(self, events):
        return ("%(ls)s" % {"ls": os.linesep}).join(
            [self._format_pool_event(e) for e in
             sorted(events, key=lambda e: e["index"])])

    def _format_progress_update(self, progress_update):
        return (
            "%(created_at)s %(message)s" % progress_update)

    def _format_progress_updates(self, progress_updates):
        return ("%(ls)s" % {"ls": os.linesep}).join(
            [self._format_progress_update(p) for p in
             sorted(progress_updates,
                    key=lambda p: (p["current_step"], p["created_at"]))])

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.name,
                obj.endpoint_id,
                obj.platform,
                obj.os_type,
                obj.status,
                obj.notes,
                obj.created_at,
                obj.updated_at,
                obj.maintenance_trust_id,
                obj.minimum_minions,
                obj.maximum_minions,
                obj.minion_max_idle_time,
                obj.minion_retention_strategy,
                cli_utils.format_json_for_object_property(
                    obj, prop_name="environment_options"),
                cli_utils.format_json_for_object_property(
                    obj, prop_name="shared_resources"),
                self._format_pool_events(obj.events),
                self._format_progress_updates(obj.progress_updates),
                cli_utils.format_json_for_object_property(
                    obj, prop_name="minion_machines"))
        return data


class CreateMinionPool(show.ShowOne):
    """ Creates a new minion pool. """
    def get_parser(self, prog_name):
        parser = super(CreateMinionPool, self).get_parser(prog_name)

        parser.add_argument('name',
                            help='A name for the new minion pool.')
        parser.add_argument('--os-type', required=True,
                            help='The OS type for the minions of the pool.')
        parser.add_argument('--platform', required=True,
                            help='The type of the minion pool ("source" or '
                                 "destination"').')
        parser.add_argument('--notes', dest='notes',
                            help='Notes about the minion pool.')
        parser.add_argument('--endpoint-id', required=True,
                            help='ID/Name of the Coriolis Endpoint to create '
                                 'the pool for.')
        parser.add_argument('--minimum-minions', type=int, default=None,
                            help='Minimum number of minions machines '
                                 'for the minion pool.')
        parser.add_argument('--maximum-minions', type=int, default=None,
                            help='Maximum number of minions machines '
                                 'for the minion pool.')
        parser.add_argument('--minion-max-idle-time', type=int, default=None,
                            help='Number of idle seconds for minions before '
                                 'being shelved based on the selected '
                                 '--minion-retention-strategy')
        parser.add_argument('--minion-retention-strategy', default='delete',
                            help='Action to take when scaling down the number '
                                 'machines within the pool.')
        parser.add_argument('--skip-allocation', action='store_true',
                            default=False,
                            help="Whether or not to skip allocating the minion"
                                 " pool's resources upfront. The pool "
                                 "allocation will need to be manually "
                                 "triggered before the pool can be used.")

        cli_utils.add_args_for_json_option_to_parser(
            parser, "environment-options")
        return parser

    def take_action(self, args):
        endpoints = self.app.client_manager.coriolis.endpoints
        endpoint_id = endpoints.get_endpoint_id_for_name(args.endpoint_id)
        environment_options = cli_utils.get_option_value_from_args(
            args, 'environment-options', error_on_no_value=True)
        minion_pool = self.app.client_manager.coriolis.minion_pools.create(
            args.name, endpoint_id, args.platform, args.os_type,
            environment_options, minimum_minions=args.minimum_minions,
            maximum_minions=args.maximum_minions,
            minion_max_idle_time=args.minion_max_idle_time,
            minion_retention_strategy=args.minion_retention_strategy,
            notes=args.notes, skip_allocation=args.skip_allocation)

        return MinionPoolDetailFormatter().get_formatted_entity(minion_pool)


class UpdateMinionPool(show.ShowOne):
    """ Updates a minion_pool. """
    def get_parser(self, prog_name):
        parser = super(UpdateMinionPool, self).get_parser(prog_name)

        parser.add_argument('id', help='The Minion Pools\'s ID.')
        parser.add_argument('--name',
                            help='New name for the new minion pool.')
        parser.add_argument('--os-type',
                            help='The OS type for the minions of the pool.')
        parser.add_argument('--notes', dest='notes',
                            help='Notes about the minion pool.')
        parser.add_argument('--minimum-minions', type=int, default=None,
                            help='Minimum number of minions machines '
                                 'for the minion pool.')
        parser.add_argument('--maximum-minions', type=int, default=None,
                            help='Maximum number of minions machines '
                                 'for the minion pool.')
        parser.add_argument('--minion-max-idle-time', type=int,
                            help='Number of idle seconds for minions before '
                                 'being shelved based on the selected '
                                 '--minion-retention-strategy')
        parser.add_argument('--minion-retention-strategy',
                            help='Action to take when scaling down the number '
                                 'machines within the pool.')
        cli_utils.add_args_for_json_option_to_parser(
            parser, "environment-options")

        return parser

    def take_action(self, args):
        updated_values = {}
        if args.name:
            updated_values["name"] = args.name
        if args.os_type:
            updated_values["os_type"] = args.os_type
        if args.minimum_minions is not None:
            updated_values["minimum_minions"] = args.minimum_minions
        if args.maximum_minions is not None:
            updated_values["maximum_minions"] = args.maximum_minions
        if args.minion_max_idle_time is not None:
            updated_values["minion_max_idle_time"] = args.minion_max_idle_time
        if args.minion_retention_strategy is not None:
            updated_values["minion_retention_strategy"] = (
                args.minion_retention_strategy)
        if args.notes:
            updated_values["notes"] = args.notes
        environment_options = cli_utils.get_option_value_from_args(
            args, 'environment-options', error_on_no_value=False)
        if environment_options:
            updated_values["environment_options"] = environment_options

        minion_pool = self.app.client_manager.coriolis.minion_pools.update(
            args.id, updated_values)

        return MinionPoolDetailFormatter().get_formatted_entity(minion_pool)


class ShowMinionPool(show.ShowOne):
    """ Show details for a Minion Pool. """

    def get_parser(self, prog_name):
        parser = super(ShowMinionPool, self).get_parser(prog_name)
        parser.add_argument('id', help='The minion_pool\'s id.')
        return parser

    def take_action(self, args):
        minion_pool = self.app.client_manager.coriolis.minion_pools.get(
            args.id)
        return MinionPoolDetailFormatter().get_formatted_entity(minion_pool)


class DeleteMinionPool(command.Command):
    """ Delete a Minion Pool. """

    def get_parser(self, prog_name):
        parser = super(DeleteMinionPool, self).get_parser(prog_name)
        parser.add_argument('id', help='The minion_pool\'s id.')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.minion_pools.delete(args.id)


class ListMinionPools(lister.Lister):
    """ List all Minion Pools. """

    def get_parser(self, prog_name):
        parser = super(ListMinionPools, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        minion_pool_list = self.app.client_manager.coriolis.minion_pools.list()
        return MinionPoolFormatter().list_objects(minion_pool_list)


class AllocateMinionPool(show.ShowOne):
    """ Allocates a Minion Pool. """

    def get_parser(self, prog_name):
        parser = super(AllocateMinionPool, self).get_parser(prog_name)
        parser.add_argument('id', help='The minion pool\'s id.')
        return parser

    def take_action(self, args):
        mps = self.app.client_manager.coriolis.minion_pools
        minion_pool = mps.allocate_minion_pool(args.id)
        return MinionPoolDetailFormatter().get_formatted_entity(minion_pool)


class RefreshMinionPool(show.ShowOne):
    """ Refreshs a Minion Pool. """

    def get_parser(self, prog_name):
        parser = super(RefreshMinionPool, self).get_parser(prog_name)
        parser.add_argument('id', help='The minion pool\'s id.')
        return parser

    def take_action(self, args):
        mps = self.app.client_manager.coriolis.minion_pools
        minion_pool = mps.refresh_minion_pool(args.id)
        return MinionPoolDetailFormatter().get_formatted_entity(minion_pool)


class DeallocateMinionPool(show.ShowOne):
    """ Deallocates a Minion Pool. """

    def get_parser(self, prog_name):
        parser = super(DeallocateMinionPool, self).get_parser(
            prog_name)
        parser.add_argument('id', help='The minion pool\'s id.')
        parser.add_argument('--force', action='store_true', default=False,
                            help='Perform a forced deallocation of the minion '
                                 'pool.')
        return parser

    def take_action(self, args):
        mps = self.app.client_manager.coriolis.minion_pools
        minion_pool = mps.deallocate_minion_pool(args.id, force=args.force)

        return MinionPoolDetailFormatter().get_formatted_entity(minion_pool)

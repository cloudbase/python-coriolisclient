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
Command-line interface sub-commands related to replicas.
"""
import argparse

from cliff import command
from cliff import lister
from cliff import show

from oslo_utils import timeutils

from coriolisclient.cli import formatter
from coriolisclient import exceptions


class RangeAction(argparse.Action):
    def __init__(self, min=None, max=None, *args, **kwargs):
        self.min = min
        self.max = max
        kwargs["metavar"] = "[%d-%d]" % (self.min, self.max)
        super(RangeAction, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        if not (self.min <= value <= self.max):
            msg = 'invalid choice: %r (choose from [%d-%d])' % \
                (value, self.min, self.max)
            raise argparse.ArgumentError(self, msg)
        setattr(namespace, self.dest, value)


class ReplicaScheduleFormatter(formatter.EntityFormatter):

    columns = ("Replica ID",
               "ID",
               "Schedule",
               "Created",
               "Expires",
               )

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.created_at)

    def _get_formatted_data(self, obj):
        data = (obj.replica_id,
                obj.id,
                obj.schedule,
                obj.created_at,
                obj.expiration_date)
        return data


class ReplicaScheduleDetailFormatter(formatter.EntityFormatter):

    columns = ("id",
               "replica_id",
               "schedule",
               "created",
               "last_updated",
               "enabled",
               "expires",
               "shutdown_instance")

    def _get_formatted_data(self, obj):
        data = (obj.id,
                obj.replica_id,
                obj.schedule,
                obj.created_at,
                obj.updated_at,
                obj.enabled,
                obj.expiration_date,
                obj.shutdown_instance)
        return data


class CreateReplicaSchedule(show.ShowOne):
    """Start a replica schedule"""
    def get_parser(self, prog_name):
        parser = super(CreateReplicaSchedule, self).get_parser(prog_name)
        parser.add_argument('replica',
                            help='The ID of the replica')
        _add_schedule_group(parser)
        parser.add_argument('--expires-at',
                            help='ISO8601 formatted date',
                            default=None)
        parser.add_argument('--disabled',
                            help='Mark this schedule as disabled on creation',
                            action='store_true',
                            default=False)
        parser.add_argument('--shutdown-instance',
                            help='Shutdown instance',
                            action='store_true',
                            default=False)
        return parser

    def take_action(self, args):
        parsed_schedule = _parse_schedule_group_args(args)
        if not any(parsed_schedule):
            raise exceptions.CoriolisException(
                "Please provide at least one value in the Schedule group")

        exp = _parse_expiration_date(args.expires_at)
        schedule = self.app.client_manager.coriolis.replica_schedules.create(
            args.replica, parsed_schedule,
            args.disabled is False, exp, args.shutdown_instance)
        return ReplicaScheduleDetailFormatter().get_formatted_entity(
            schedule)


class ShowReplicaSchedule(show.ShowOne):
    """Show a replica schedule"""

    def get_parser(self, prog_name):
        parser = super(ShowReplicaSchedule, self).get_parser(prog_name)
        parser.add_argument('replica', help='The replica\'s id')
        parser.add_argument('id', help='The replica schedule\'s id')
        return parser

    def take_action(self, args):
        schedule = self.app.client_manager.coriolis.replica_schedules.get(
            args.replica, args.id)
        return ReplicaScheduleDetailFormatter().get_formatted_entity(
            schedule)


class UpdateReplicaSchedule(show.ShowOne):
    """Updates a replica schedule"""
    def get_parser(self, prog_name):
        parser = super(UpdateReplicaSchedule, self).get_parser(prog_name)
        parser.add_argument('replica', help='The replica\'s id')
        parser.add_argument('id', help='The replica schedule\'s id')
        _add_schedule_group(parser)
        expires_parser = parser.add_mutually_exclusive_group(required=False)
        expires_parser.add_argument(
            '--expires-at',
            help='ISO8601 formatted date. This is optional',
            dest="expires",
            default=None)
        expires_parser.add_argument(
            '--no-expiration-date',
            help='Clear expiration date',
            dest="expires",
            const=False,
            action="store_const")
        enabled_parser = parser.add_mutually_exclusive_group(required=False)
        enabled_parser.add_argument(
            '--disabled',
            help='Mark this task as disabled',
            dest='enabled',
            action='store_false',
            default=None)
        enabled_parser.add_argument(
            '--enabled',
            help='Mark this task as enabled',
            dest='enabled',
            action='store_true',
            default=None)
        shutdown_parser = parser.add_mutually_exclusive_group(required=False)
        shutdown_parser.add_argument(
            '--shutdown-instance',
            help='Shutdown instance',
            dest="shutdown",
            action='store_true')
        shutdown_parser.add_argument(
            '--dont-shutdown-instance',
            help="Don't shutdown instance",
            dest="shutdown",
            action='store_false')
        return parser

    def take_action(self, args):
        updated_values = {}

        parsed_schedule = _parse_schedule_group_args(args)
        if len(parsed_schedule):
            updated_values["schedule"] = parsed_schedule

        if args.expires is not None:
            if args.expires is False:
                updated_values["expiration_date"] = None
            else:
                exp = _parse_expiration_date(args.expires)
                updated_values["expiration_date"] = exp
        if args.shutdown is not None:
            updated_values["shutdown_instance"] = args.shutdown
        if args.enabled is not None:
            updated_values["enabled"] = args.enabled

        schedule = self.app.client_manager.coriolis.replica_schedules.update(
            args.replica, args.id, updated_values)

        return ReplicaScheduleDetailFormatter().get_formatted_entity(
            schedule)


class DeleteReplicaSchedule(command.Command):
    """Delete a replica schedule"""

    def get_parser(self, prog_name):
        parser = super(DeleteReplicaSchedule, self).get_parser(prog_name)
        parser.add_argument('replica', help='The replica\'s id')
        parser.add_argument('id', help='The replica schedule\'s id')
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.replica_schedules.delete(
            args.replica, args.id)


class ListReplicaSchedule(lister.Lister):
    """List replica schedules"""

    def get_parser(self, prog_name):
        parser = super(ListReplicaSchedule, self).get_parser(prog_name)
        parser.add_argument('replica', help='The replica\'s id')
        parser.add_argument('--hide-expired',
                            help='Hide expired schedules',
                            action='store_true',
                            default=False)
        return parser

    def take_action(self, args):
        obj_list = self.app.client_manager.coriolis.replica_schedules.list(
            args.replica, hide_expired=args.hide_expired)
        return ReplicaScheduleFormatter().list_objects(obj_list)


def _add_schedule_group(parser):
    group = parser.add_argument_group('Schedule')
    group.add_argument('-M', '--minute',
                       help='The minute of the hour at which to run',
                       dest="minute",
                       type=int,
                       action=RangeAction,
                       min=0,
                       max=59,
                       default=None)
    group.add_argument('-H', '--hour',
                       help='The hour of the day at which to run. '
                       'UTC time is required',
                       dest="hour",
                       type=int,
                       min=0,
                       max=23,
                       action=RangeAction,
                       default=None)
    group.add_argument('-d', '--day-of-month',
                       help='The day of the month at which to run',
                       dest="dom",
                       type=int,
                       min=1,
                       max=31,
                       action=RangeAction,
                       default=None)
    group.add_argument('-m', '--month',
                       help='The month in which to run',
                       dest="month",
                       type=int,
                       min=1,
                       max=12,
                       action=RangeAction,
                       default=None)
    group.add_argument('-w', '--day-of-week',
                       help='The day of week in which to run',
                       dest="dow",
                       type=int,
                       min=0,
                       max=6,
                       action=RangeAction,
                       default=None)


def _parse_schedule_group_args(args):
    parsed_schedule = {}
    for field in ("minute", "hour", "dom", "month", "dow"):
        val = getattr(args, field)
        if val is not None:
            parsed_schedule[field] = val
    return parsed_schedule


def _parse_expiration_date(value):
    if value is None:
        return
    try:
        return timeutils.normalize_time(timeutils.parse_isotime(value))
    except Exception as err:
        raise exceptions.CoriolisException(
            "Invalid expiration date: %s" % err)

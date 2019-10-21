# Copyright (c) 2019 Cloudbase Solutions Srl
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
Command-line interface sub-commands related to logging.
"""
import argparse

from cliff import command
from cliff import lister
from cliff import show

from oslo_utils import timeutils

from coriolisclient.cli import formatter
from coriolisclient import exceptions


_READIBLE_LOG_LEVELS = [
    "EMERGENCY",
    "ALERT",
    "CRITICAL",
    "ERROR",
    "WARNING",
    "NOTICE",
    "INFO",
    "DEBUG",
]

_MAPPED_LOG_LEVELS = {
    "EMERGENCY": 0,
    "ALERT": 1,
    "CRITICAL": 2,
    "ERROR": 3,
    "WARNING": 4,
    "NOTICE": 5,
    "INFO": 6,
    "DEBUG": 7,
}

_DEFAULT_LOG_LEVEL = _MAPPED_LOG_LEVELS["INFO"]


class LogsFormatter(formatter.EntityFormatter):

    columns = ("Log name",)

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o.log_name)

    def _get_formatted_data(self, obj):
        data = (obj.log_name,)
        return data


class ListCoriolisLogs(lister.Lister):
    """Get a list of available logs"""

    def get_parser(self, prog_name):
        parser = super(ListCoriolisLogs, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        logs = self.app.client_manager.coriolis.logging.list()
        return LogsFormatter().list_objects(
            logs)


class DownloadCoriolisLog(command.Command):

    def get_parser(self, prog_name):
        parser = super(DownloadCoriolisLog, self).get_parser(prog_name)
        parser.add_argument(
            'log_name',
            help='The name of the log to fetch')
        parser.add_argument(
            '--start-time',
            help="The start date of the log. This can be a unix timestamp"
            " or a period written as one of the following:"
            " 1s, 1m, 1h, 1d, 1w",
            default=None)
        parser.add_argument(
            '--end-time',
            help="The end date of the log. This can be a unix timestamp"
            " or a period written as one of the following:"
            " 1s, 1m, 1h, 1d, 1w",
            default=None)
        parser.add_argument(
            '--out-file',
            help="The destination file name where the log will be written",
            required=True)
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.logging.get(
            args.log_name, args.out_file,
            start_time=args.start_time, end_time=args.end_time)


class StreamCoriolisLog(command.Command):

    def get_parser(self, prog_name):
        parser = super(StreamCoriolisLog, self).get_parser(prog_name)
        parser.add_argument(
            '--log-name',
            required=False,
            help='The name of the log to stream')
        parser.add_argument(
            '--severity',
            help="The desired log level of the streamed logs",
            required=False,
            default=_DEFAULT_LOG_LEVEL,
            choices=_READIBLE_LOG_LEVELS)
        return parser

    def take_action(self, args):
        self.app.client_manager.coriolis.logging.stream(
            app_name=args.log_name,
            severity=_MAPPED_LOG_LEVELS[args.severity])

# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from cliff import command
from cliff import lister

from coriolisclient.cli import logging
from coriolisclient.tests import test_base


class LogsFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Logs Formatter."""

    def setUp(self):
        super(LogsFormatterTestCase, self).setUp()
        self.logger = logging.LogsFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.log_name = "log1"
        obj2.log_name = "log2"
        obj3.log_name = "log3"
        obj_list = [obj2, obj1, obj3]

        result = self.logger._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.log_name = mock.sentinel.log_name

        result = self.logger._get_formatted_data(obj)

        self.assertEqual(
            (mock.sentinel.log_name,),
            result
        )


class ListCoriolisLogsTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Coriolis Logs."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListCoriolisLogsTestCase, self).setUp()
        self.logger = logging.ListCoriolisLogs(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.logger.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(logging.LogsFormatter, 'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        mock_logging = mock.Mock()
        self.mock_app.client_manager.coriolis.logging.list = mock_logging

        result = self.logger.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_list_objects.assert_called_once_with(mock_logging.return_value)


class DownloadCoriolisLogTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Download Coriolis Log."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DownloadCoriolisLogTestCase, self).setUp()
        self.logger = logging.DownloadCoriolisLog(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.logger.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.log_name = mock.sentinel.log_name
        args.out_file = mock.sentinel.out_file
        args.start_time = mock.sentinel.start_time
        args.end_time = mock.sentinel.end_time
        mock_logging = mock.Mock()
        self.mock_app.client_manager.coriolis.logging.get = mock_logging

        self.logger.take_action(args)

        mock_logging.assert_called_once_with(
            mock.sentinel.log_name,
            mock.sentinel.out_file,
            start_time=mock.sentinel.start_time,
            end_time=mock.sentinel.end_time
        )


class StreamCoriolisLogTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Stream Coriolis Log."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(StreamCoriolisLogTestCase, self).setUp()
        self.logger = logging.StreamCoriolisLog(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.logger.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.log_name = mock.sentinel.log_name
        args.severity = "INFO"
        mock_logging = mock.Mock()
        self.mock_app.client_manager.coriolis.logging.stream = mock_logging

        self.logger.take_action(args)

        mock_logging.assert_called_once_with(
            app_name=mock.sentinel.log_name,
            severity=6
        )

# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import argparse
import datetime
from unittest import mock

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import transfer_schedules
from coriolisclient import exceptions
from coriolisclient.tests import test_base


class RangeActionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Transfer Range Action."""

    def setUp(self):
        super(RangeActionTestCase, self).setUp()
        self.range_action = transfer_schedules.RangeAction(
            1, 10, ["mock_option"], "dest")

    def test__call__(self):
        mock_parser = mock.Mock()
        mock_namespace = mock.Mock()
        value = 5

        self.range_action(mock_parser, mock_namespace, value)

        self.assertEqual(
            value,
            mock_namespace.dest
        )

    def test__call__argument_error(self):
        mock_parser = mock.Mock()
        mock_namespace = mock.Mock()
        value = -1

        self.assertRaises(
            argparse.ArgumentError,
            self.range_action,
            mock_parser,
            mock_namespace,
            value
        )


class TransferScheduleFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Transfer Schedule Formatter."""

    def setUp(self):
        super(TransferScheduleFormatterTestCase, self).setUp()
        self.transfer_schedules = (
            transfer_schedules.TransferScheduleFormatter())

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.created_at = "date1"
        obj2.created_at = "date2"
        obj3.created_at = "date3"
        obj_list = [obj2, obj1, obj3]

        result = self.transfer_schedules._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.transfer_id = mock.sentinel.transfer_id
        obj.id = mock.sentinel.id
        obj.schedule = mock.sentinel.schedule
        obj.created_at = mock.sentinel.created_at
        obj.expiration_date = mock.sentinel.expiration_date

        result = self.transfer_schedules._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.transfer_id,
                mock.sentinel.id,
                mock.sentinel.schedule,
                mock.sentinel.created_at,
                mock.sentinel.expiration_date
            ),
            result
        )


class TransferScheduleDetailFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Transfer Schedule Detail Formatter."""

    def setUp(self):
        super(TransferScheduleDetailFormatterTestCase, self).setUp()
        self.transfer_schedules = (
            transfer_schedules.TransferScheduleDetailFormatter())

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.transfer_id = mock.sentinel.transfer_id
        obj.schedule = mock.sentinel.schedule
        obj.created_at = mock.sentinel.created_at
        obj.updated_at = mock.sentinel.updated_at
        obj.enabled = False
        obj.expiration_date = mock.sentinel.expiration_date
        obj.shutdown_instance = mock.sentinel.shutdown_instance
        obj.auto_deploy = mock.sentinel.auto_deploy

        result = self.transfer_schedules._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.transfer_id,
                mock.sentinel.schedule,
                mock.sentinel.created_at,
                mock.sentinel.updated_at,
                False,
                mock.sentinel.expiration_date,
                mock.sentinel.shutdown_instance,
                mock.sentinel.auto_deploy,
            ),
            result
        )


class CreateTransferScheduleTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Create Transfer Schedule."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CreateTransferScheduleTestCase, self).setUp()
        self.transfer_schedules = transfer_schedules.CreateTransferSchedule(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.transfer_schedules.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfer_schedules.TransferScheduleDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(transfer_schedules, '_parse_expiration_date')
    @mock.patch.object(transfer_schedules, '_parse_schedule_group_args')
    def test_take_action(
        self,
        mock_parse_schedule_group_args,
        mock_parse_expiration_date,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.transfer = mock.sentinel.transfer
        args.disabled = False
        args.shutdown_instance = False
        args.auto_deploy = False
        mock_schedule_group_args = {"minute": mock.sentinel.minute}
        mock_parse_schedule_group_args.return_value = mock_schedule_group_args
        mock_schedule = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_schedules.create = \
            mock_schedule

        result = self.transfer_schedules.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_schedule.assert_called_once_with(
            mock.sentinel.transfer,
            mock_schedule_group_args,
            True,
            mock_parse_expiration_date.return_value,
            False,
            False,
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_schedule.return_value)

    @mock.patch.object(transfer_schedules, '_parse_expiration_date')
    @mock.patch.object(transfer_schedules, '_parse_schedule_group_args')
    def test_take_action_no_parsed_schedule(
        self,
        mock_parse_schedule_group_args,
        mock_parse_expiration_date
    ):
        args = mock.Mock()
        mock_parse_schedule_group_args.return_value = {}

        self.assertRaises(
            exceptions.CoriolisException,
            self.transfer_schedules.take_action,
            args
        )
        mock_parse_expiration_date.assert_not_called()


class ShowTransferScheduleTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Show Transfer Schedule."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ShowTransferScheduleTestCase, self).setUp()
        self.transfer_schedules = transfer_schedules.ShowTransferSchedule(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.transfer_schedules.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfer_schedules.TransferScheduleDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.transfer = mock.sentinel.transfer
        args.id = mock.sentinel.id
        schedule = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_schedules.get = \
            schedule

        result = self.transfer_schedules.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        schedule.assert_called_once_with(args.transfer, args.id)
        mock_get_formatted_entity.assert_called_once_with(
            schedule.return_value)


class UpdateTransferScheduleTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Update Transfer Schedule."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(UpdateTransferScheduleTestCase, self).setUp()
        self.transfer_schedules = transfer_schedules.UpdateTransferSchedule(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.transfer_schedules.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfer_schedules.TransferScheduleDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(transfer_schedules, '_parse_expiration_date')
    @mock.patch.object(transfer_schedules, '_parse_schedule_group_args')
    def test_take_action(
        self,
        mock_parse_schedule_group_args,
        mock_parse_expiration_date,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.expires = True
        args.shutdown = True
        args.enabled = True
        args.transfer = mock.sentinel.transfer
        args.id = mock.sentinel.id
        args.auto_deploy = False
        mock_parse_schedule_group_args.return_value = \
            {"minute": mock.sentinel.minute}
        transfer_schedule = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_schedules = \
            transfer_schedule
        expected_updated_values = {
            "schedule": {"minute": mock.sentinel.minute},
            "expiration_date": mock_parse_expiration_date.return_value,
            "shutdown_instance": True,
            "enabled": True,
            "auto_deploy": False,
        }

        result = self.transfer_schedules.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )

        transfer_schedule.update.assert_called_once_with(
            mock.sentinel.transfer,
            mock.sentinel.id,
            expected_updated_values
        )

    @mock.patch.object(transfer_schedules.TransferScheduleDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(transfer_schedules, '_parse_expiration_date')
    @mock.patch.object(transfer_schedules, '_parse_schedule_group_args')
    def test_take_action_no_updated_values(
        self,
        mock_parse_schedule_group_args,
        mock_parse_expiration_date,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.transfer = mock.sentinel.transfer
        args.id = mock.sentinel.id
        args.expires = False
        args.shutdown = None
        args.enabled = None
        args.auto_deploy = None
        mock_parse_schedule_group_args.return_value = {}
        transfer_schedule = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_schedules = \
            transfer_schedule
        expected_updated_values = {"expiration_date": None}

        result = self.transfer_schedules.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )

        mock_parse_expiration_date.assert_not_called()
        transfer_schedule.update.assert_called_once_with(
            mock.sentinel.transfer,
            mock.sentinel.id,
            expected_updated_values
        )


class DeleteTransferScheduleTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Delete Transfer Schedule."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeleteTransferScheduleTestCase, self).setUp()
        self.transfer_schedules = transfer_schedules.DeleteTransferSchedule(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.transfer_schedules.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.transfer = mock.sentinel.transfer
        args.id = mock.sentinel.id
        transfer_schedule = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_schedules = \
            transfer_schedule

        self.transfer_schedules.take_action(args)

        transfer_schedule.delete.assert_called_once_with(
            mock.sentinel.transfer, mock.sentinel.id)


class ListTransferScheduleTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Transfer Schedule."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListTransferScheduleTestCase, self).setUp()
        self.transfer_schedules = transfer_schedules.ListTransferSchedule(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.transfer_schedules.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfer_schedules.TransferScheduleFormatter,
                       'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        args.transfer = mock.sentinel.transfer
        args.hide_expired = mock.sentinel.hide_expired
        mock_transfer_list = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_schedules.list = \
            mock_transfer_list

        result = self.transfer_schedules.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_transfer_list.assert_called_once_with(
            mock.sentinel.transfer, hide_expired=mock.sentinel.hide_expired)
        mock_list_objects.assert_called_once_with(
            mock_transfer_list.return_value)


class TransferSchedulesTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Transfer Schedules."""

    def test_add_schedule_group(self):
        parser = argparse.ArgumentParser()

        transfer_schedules._add_schedule_group(parser)

        self.assertIn(
            "Schedule",
            [g.title for g in parser._action_groups]
        )

    def test_parse_schedule_group_args(self):
        class CustomMock(mock.MagicMock):
            def __getattr__(self, name):
                return None
        args = CustomMock()
        args.minute = mock.sentinel.minute
        args.hour = mock.sentinel.hour
        expected_result = {
            "minute": mock.sentinel.minute,
            "hour": mock.sentinel.hour
        }

        result = transfer_schedules._parse_schedule_group_args(args)

        self.assertEqual(
            expected_result,
            result
        )

    def test_parse_expiration_date(self):
        value = None

        result = transfer_schedules._parse_expiration_date(value)

        self.assertEqual(
            None,
            result
        )

        value = "2099-12-31"

        result = transfer_schedules._parse_expiration_date(value)

        self.assertEqual(
            datetime.datetime(2099, 12, 31, 0, 0),
            result
        )

        value = "2099-31-12"

        self.assertRaises(
            exceptions.CoriolisException,
            transfer_schedules._parse_expiration_date,
            value
        )

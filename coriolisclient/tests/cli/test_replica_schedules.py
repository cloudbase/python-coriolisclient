# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import argparse
import datetime
from unittest import mock

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import replica_schedules
from coriolisclient import exceptions
from coriolisclient.tests import test_base


class RangeActionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Replica Range Action."""

    def setUp(self):
        super(RangeActionTestCase, self).setUp()
        self.range_action = replica_schedules.RangeAction(
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


class ReplicaScheduleFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Replica Schedule Formatter."""

    def setUp(self):
        super(ReplicaScheduleFormatterTestCase, self).setUp()
        self.replica = replica_schedules.ReplicaScheduleFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.created_at = "date1"
        obj2.created_at = "date2"
        obj3.created_at = "date3"
        obj_list = [obj2, obj1, obj3]

        result = self.replica._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.replica_id = mock.sentinel.replica_id
        obj.id = mock.sentinel.id
        obj.schedule = mock.sentinel.schedule
        obj.created_at = mock.sentinel.created_at
        obj.expiration_date = mock.sentinel.expiration_date

        result = self.replica._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.replica_id,
                mock.sentinel.id,
                mock.sentinel.schedule,
                mock.sentinel.created_at,
                mock.sentinel.expiration_date
            ),
            result
        )


class ReplicaScheduleDetailFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Replica Schedule Detail Formatter."""

    def setUp(self):
        super(ReplicaScheduleDetailFormatterTestCase, self).setUp()
        self.replica = replica_schedules.ReplicaScheduleDetailFormatter()

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.replica_id = mock.sentinel.replica_id
        obj.schedule = mock.sentinel.schedule
        obj.created_at = mock.sentinel.created_at
        obj.updated_at = mock.sentinel.updated_at
        obj.enabled = False
        obj.expiration_date = mock.sentinel.expiration_date
        obj.shutdown_instance = mock.sentinel.shutdown_instance

        result = self.replica._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.replica_id,
                mock.sentinel.schedule,
                mock.sentinel.created_at,
                mock.sentinel.updated_at,
                False,
                mock.sentinel.expiration_date,
                mock.sentinel.shutdown_instance
            ),
            result
        )


class CreateReplicaScheduleTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Create Replica Schedule."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CreateReplicaScheduleTestCase, self).setUp()
        self.replica = replica_schedules.CreateReplicaSchedule(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.replica.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(replica_schedules.ReplicaScheduleDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(replica_schedules, '_parse_expiration_date')
    @mock.patch.object(replica_schedules, '_parse_schedule_group_args')
    def test_take_action(
        self,
        mock_parse_schedule_group_args,
        mock_parse_expiration_date,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.replica = mock.sentinel.replica
        args.disabled = False
        args.shutdown_instance = mock.sentinel.shutdown_instance
        mock_schedule_group_args = {"minute": mock.sentinel.minute}
        mock_parse_schedule_group_args.return_value = mock_schedule_group_args
        mock_schedule = mock.Mock()
        self.mock_app.client_manager.coriolis.replica_schedules.create = \
            mock_schedule

        result = self.replica.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_schedule.assert_called_once_with(
            mock.sentinel.replica,
            mock_schedule_group_args,
            True,
            mock_parse_expiration_date.return_value,
            mock.sentinel.shutdown_instance
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_schedule.return_value)

    @mock.patch.object(replica_schedules, '_parse_expiration_date')
    @mock.patch.object(replica_schedules, '_parse_schedule_group_args')
    def test_take_action_no_parsed_schedule(
        self,
        mock_parse_schedule_group_args,
        mock_parse_expiration_date
    ):
        args = mock.Mock()
        mock_parse_schedule_group_args.return_value = {}

        self.assertRaises(
            exceptions.CoriolisException,
            self.replica.take_action,
            args
        )
        mock_parse_expiration_date.assert_not_called()


class ShowReplicaScheduleTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Show Replica Schedule."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ShowReplicaScheduleTestCase, self).setUp()
        self.replica = replica_schedules.ShowReplicaSchedule(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.replica.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(replica_schedules.ReplicaScheduleDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.replica = mock.sentinel.replica
        args.id = mock.sentinel.id
        schedule = mock.Mock()
        self.mock_app.client_manager.coriolis.replica_schedules.get = \
            schedule

        result = self.replica.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        schedule.assert_called_once_with(args.replica, args.id)
        mock_get_formatted_entity.assert_called_once_with(
            schedule.return_value)


class UpdateReplicaScheduleTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Update Replica Schedule."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(UpdateReplicaScheduleTestCase, self).setUp()
        self.replica = replica_schedules.UpdateReplicaSchedule(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.replica.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(replica_schedules.ReplicaScheduleDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(replica_schedules, '_parse_expiration_date')
    @mock.patch.object(replica_schedules, '_parse_schedule_group_args')
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
        args.replica = mock.sentinel.replica
        args.id = mock.sentinel.id
        mock_parse_schedule_group_args.return_value = \
            {"minute": mock.sentinel.minute}
        replica_schedule = mock.Mock()
        self.mock_app.client_manager.coriolis.replica_schedules = \
            replica_schedule
        expected_updated_values = {
            "schedule": {"minute": mock.sentinel.minute},
            "expiration_date": mock_parse_expiration_date.return_value,
            "shutdown_instance": True,
            "enabled": True,
        }

        result = self.replica.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )

        replica_schedule.update.assert_called_once_with(
            mock.sentinel.replica,
            mock.sentinel.id,
            expected_updated_values
        )

    @mock.patch.object(replica_schedules.ReplicaScheduleDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(replica_schedules, '_parse_expiration_date')
    @mock.patch.object(replica_schedules, '_parse_schedule_group_args')
    def test_take_action_no_updated_values(
        self,
        mock_parse_schedule_group_args,
        mock_parse_expiration_date,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.replica = mock.sentinel.replica
        args.id = mock.sentinel.id
        args.expires = False
        args.shutdown = None
        args.enabled = None
        mock_parse_schedule_group_args.return_value = {}
        replica_schedule = mock.Mock()
        self.mock_app.client_manager.coriolis.replica_schedules = \
            replica_schedule
        expected_updated_values = {"expiration_date": None}

        result = self.replica.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )

        mock_parse_expiration_date.assert_not_called()
        replica_schedule.update.assert_called_once_with(
            mock.sentinel.replica,
            mock.sentinel.id,
            expected_updated_values
        )


class DeleteReplicaScheduleTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Delete Replica Schedule."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeleteReplicaScheduleTestCase, self).setUp()
        self.replica = replica_schedules.DeleteReplicaSchedule(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.replica.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.replica = mock.sentinel.replica
        args.id = mock.sentinel.id
        replica_schedule = mock.Mock()
        self.mock_app.client_manager.coriolis.replica_schedules = \
            replica_schedule

        self.replica.take_action(args)

        replica_schedule.delete.assert_called_once_with(
            mock.sentinel.replica, mock.sentinel.id)


class ListReplicaScheduleTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Replica Schedule."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListReplicaScheduleTestCase, self).setUp()
        self.replica = replica_schedules.ListReplicaSchedule(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.replica.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(replica_schedules.ReplicaScheduleFormatter,
                       'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        args.replica = mock.sentinel.replica
        args.hide_expired = mock.sentinel.hide_expired
        mock_replica_list = mock.Mock()
        self.mock_app.client_manager.coriolis.replica_schedules.list = \
            mock_replica_list

        result = self.replica.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_replica_list.assert_called_once_with(
            mock.sentinel.replica, hide_expired=mock.sentinel.hide_expired)
        mock_list_objects.assert_called_once_with(
            mock_replica_list.return_value)


class ReplicaSchedulesTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Replica Schedules."""

    def test_add_schedule_group(self):
        parser = argparse.ArgumentParser()

        replica_schedules._add_schedule_group(parser)

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

        result = replica_schedules._parse_schedule_group_args(args)

        self.assertEqual(
            expected_result,
            result
        )

    def test_parse_expiration_date(self):
        value = None

        result = replica_schedules._parse_expiration_date(value)

        self.assertEqual(
            None,
            result
        )

        value = "2099-12-31"

        result = replica_schedules._parse_expiration_date(value)

        self.assertEqual(
            datetime.datetime(2099, 12, 31, 0, 0),
            result
        )

        value = "2099-31-12"

        self.assertRaises(
            exceptions.CoriolisException,
            replica_schedules._parse_expiration_date,
            value
        )

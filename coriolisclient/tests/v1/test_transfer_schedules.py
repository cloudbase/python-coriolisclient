# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import datetime
from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import transfer_schedules


class TransferScheduleManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Transfer Schedule Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(TransferScheduleManagerTestCase, self).setUp()
        self.transfer_schedule = transfer_schedules.TransferScheduleManager(
            mock_client)

    @mock.patch.object(transfer_schedules.TransferScheduleManager, "_list")
    def test_list(self, mock_list):
        result = self.transfer_schedule.list(
            mock.sentinel.transfer, hide_expired=False)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            '/transfers/%s/schedules' % mock.sentinel.transfer, "schedules")

    @mock.patch.object(transfer_schedules.TransferScheduleManager, "_list")
    def test_list_hide_expired(self, mock_list):
        result = self.transfer_schedule.list(
            mock.sentinel.transfer, hide_expired=True)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            '/transfers/%s/schedules?show_expired=False'
            % mock.sentinel.transfer, "schedules")

    @mock.patch.object(transfer_schedules.TransferScheduleManager, "_get")
    def test_get(self, mock_get):
        result = self.transfer_schedule.get(
            mock.sentinel.transfer, mock.sentinel.schedule)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            "/transfers/%s/schedules/%s" % (mock.sentinel.transfer,
                                            mock.sentinel.schedule),
            "schedule")

    @mock.patch.object(transfer_schedules.TransferScheduleManager, "_post")
    def test_create(self, mock_post):
        expiration_date = datetime.datetime.fromisoformat("2034-11-26")
        expected_data = {
            "schedule": mock.sentinel.schedule,
            "enabled": True,
            "expiration_date": '2034-11-26T00:00:00Z',
            "shutdown_instance": mock.sentinel.shutdown_instance,
            "auto_deploy": mock.sentinel.auto_deploy,
        }

        result = self.transfer_schedule.create(
            mock.sentinel.transfer,
            mock.sentinel.schedule,
            True,
            expiration_date,
            mock.sentinel.shutdown_instance,
            mock.sentinel.auto_deploy,
        )

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            '/transfers/%s/schedules' % mock.sentinel.transfer,
            expected_data, "schedule")

    @mock.patch.object(transfer_schedules.TransferScheduleManager, "_put")
    def test_update(self, mock_put):
        expiration_date = datetime.datetime.fromisoformat("2034-11-26")
        updated_values = {"expiration_date": expiration_date}
        result = self.transfer_schedule.update(
            mock.sentinel.transfer_id,
            mock.sentinel.schedule_id,
            updated_values
        )

        self.assertEqual(
            mock_put.return_value,
            result
        )
        mock_put.assert_called_once_with(
            "/transfers/%s/schedules/%s" % (mock.sentinel.transfer_id,
                                            mock.sentinel.schedule_id),
            {"expiration_date": '2034-11-26T00:00:00Z'},
            "schedule")

    @mock.patch.object(transfer_schedules.TransferScheduleManager, "_delete")
    def test_delete(self, mock_delete):
        result = self.transfer_schedule.delete(
            mock.sentinel.transfer, mock.sentinel.schedule)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            "/transfers/%s/schedules/%s" % (mock.sentinel.transfer,
                                            mock.sentinel.schedule),)

    def test_format_rfc3339_datetime(self):
        dt = datetime.date(2024, 1, 1)

        result = self.transfer_schedule._format_rfc3339_datetime(dt)

        self.assertEqual(
            "2024-01-01Z",
            result
        )

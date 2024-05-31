# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import datetime
from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import replica_schedules


class ReplicaScheduleManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Replica Schedule Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(ReplicaScheduleManagerTestCase, self).setUp()
        self.replica_schedule = replica_schedules.ReplicaScheduleManager(
            mock_client)

    @mock.patch.object(replica_schedules.ReplicaScheduleManager, "_list")
    def test_list(self, mock_list):
        result = self.replica_schedule.list(
            mock.sentinel.replica, hide_expired=False)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            '/replicas/%s/schedules' % mock.sentinel.replica, "schedules")

    @mock.patch.object(replica_schedules.ReplicaScheduleManager, "_list")
    def test_list_hide_expired(self, mock_list):
        result = self.replica_schedule.list(
            mock.sentinel.replica, hide_expired=True)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            '/replicas/%s/schedules?show_expired=False'
            % mock.sentinel.replica, "schedules")

    @mock.patch.object(replica_schedules.ReplicaScheduleManager, "_get")
    def test_get(self, mock_get):
        result = self.replica_schedule.get(
            mock.sentinel.replica, mock.sentinel.schedule)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            "/replicas/%s/schedules/%s" % (mock.sentinel.replica,
                                           mock.sentinel.schedule),
            "schedule")

    @mock.patch.object(replica_schedules.ReplicaScheduleManager, "_post")
    def test_create(self, mock_post):
        expiration_date = datetime.datetime.fromisoformat("2034-11-26")
        expected_data = {
            "schedule": mock.sentinel.schedule,
            "enabled": True,
            "expiration_date": '2034-11-26T00:00:00Z',
            "shutdown_instance": mock.sentinel.shutdown_instance
        }

        result = self.replica_schedule.create(
            mock.sentinel.replica,
            mock.sentinel.schedule,
            True,
            expiration_date,
            mock.sentinel.shutdown_instance
        )

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            '/replicas/%s/schedules' % mock.sentinel.replica,
            expected_data, "schedule")

    @mock.patch.object(replica_schedules.ReplicaScheduleManager, "_put")
    def test_update(self, mock_put):
        expiration_date = datetime.datetime.fromisoformat("2034-11-26")
        updated_values = {"expiration_date": expiration_date}
        result = self.replica_schedule.update(
            mock.sentinel.replica_id,
            mock.sentinel.schedule_id,
            updated_values
        )

        self.assertEqual(
            mock_put.return_value,
            result
        )
        mock_put.assert_called_once_with(
            "/replicas/%s/schedules/%s" % (mock.sentinel.replica_id,
                                           mock.sentinel.schedule_id),
            {"expiration_date": '2034-11-26T00:00:00Z'},
            "schedule")

    @mock.patch.object(replica_schedules.ReplicaScheduleManager, "_delete")
    def test_delete(self, mock_delete):
        result = self.replica_schedule.delete(
            mock.sentinel.replica, mock.sentinel.schedule)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            "/replicas/%s/schedules/%s" % (mock.sentinel.replica,
                                           mock.sentinel.schedule),)

    def test_format_rfc3339_datetime(self):
        dt = datetime.date(2024, 1, 1)

        result = self.replica_schedule._format_rfc3339_datetime(dt)

        self.assertEqual(
            "2024-01-01Z",
            result
        )

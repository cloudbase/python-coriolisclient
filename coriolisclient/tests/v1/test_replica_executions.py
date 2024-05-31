# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import replica_executions


class ReplicaExecutionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Replica Execution."""

    def test_tasks(self):
        mock_client = mock.Mock()
        self.replica_execution = replica_executions.ReplicaExecution(
            mock_client,
            {
                "tasks": [{"task1": mock.sentinel.task1},
                          {"task2": mock.sentinel.task2}],
            }
        )
        self.assertEqual(
            (
                mock.sentinel.task1,
                mock.sentinel.task2
            ),
            (
                self.replica_execution.tasks[0].task1,
                self.replica_execution.tasks[1].task2
            )
        )


class ReplicaExecutionManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Replica Execution Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(ReplicaExecutionManagerTestCase, self).setUp()
        self.replica_execution = replica_executions.ReplicaExecutionManager(
            mock_client)

    @mock.patch.object(replica_executions.ReplicaExecutionManager, "_list")
    def test_list(self, mock_list):
        result = self.replica_execution.list(mock.sentinel.replica)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            '/replicas/%s/executions' % mock.sentinel.replica, "executions")

    @mock.patch.object(replica_executions.ReplicaExecutionManager, "_get")
    def test_get(self, mock_get):
        result = self.replica_execution.get(
            mock.sentinel.replica, mock.sentinel.execution)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            "/replicas/%s/executions/%s" % (mock.sentinel.replica,
                                            mock.sentinel.execution),
            "execution")

    @mock.patch.object(replica_executions.ReplicaExecutionManager, "_post")
    def test_create(self, mock_post):
        expected_data = {
            "shutdown_instances": mock.sentinel.shutdown_instances
        }
        expected_data = {"execution": expected_data}

        result = self.replica_execution.create(
            mock.sentinel.replica,
            shutdown_instances=mock.sentinel.shutdown_instances
        )

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            '/replicas/%s/executions' % mock.sentinel.replica,
            expected_data, "execution")

    @mock.patch.object(replica_executions.ReplicaExecutionManager, "_delete")
    def test_delete(self, mock_delete):
        result = self.replica_execution.delete(
            mock.sentinel.replica, mock.sentinel.execution)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            "/replicas/%s/executions/%s" % (mock.sentinel.replica,
                                            mock.sentinel.execution),)

    def test_cancel(self):
        result = self.replica_execution.cancel(
            mock.sentinel.replica, mock.sentinel.execution, force=False)

        self.assertEqual(
            self.replica_execution.client.post.return_value,
            result
        )
        self.replica_execution.client.post.assert_called_once_with(
            "/replicas/%s/executions/%s/actions" % (mock.sentinel.replica,
                                                    mock.sentinel.execution),
            json={'cancel': {'force': False}})

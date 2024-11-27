# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import transfer_executions


class TransferExecutionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Transfer Execution."""

    def test_tasks(self):
        mock_client = mock.Mock()
        self.transfer_execution = transfer_executions.TransferExecution(
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
                self.transfer_execution.tasks[0].task1,
                self.transfer_execution.tasks[1].task2
            )
        )


class TransferExecutionManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Transfer Execution Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(TransferExecutionManagerTestCase, self).setUp()
        self.transfer_execution = transfer_executions.TransferExecutionManager(
            mock_client)

    @mock.patch.object(transfer_executions.TransferExecutionManager, "_list")
    def test_list(self, mock_list):
        result = self.transfer_execution.list(mock.sentinel.transfer)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            '/transfers/%s/executions' % mock.sentinel.transfer, "executions")

    @mock.patch.object(transfer_executions.TransferExecutionManager, "_get")
    def test_get(self, mock_get):
        result = self.transfer_execution.get(
            mock.sentinel.transfer, mock.sentinel.execution)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            "/transfers/%s/executions/%s" % (mock.sentinel.transfer,
                                             mock.sentinel.execution),
            "execution")

    @mock.patch.object(transfer_executions.TransferExecutionManager, "_post")
    def test_create(self, mock_post):
        expected_data = {
            "shutdown_instances": mock.sentinel.shutdown_instances
        }
        expected_data = {"execution": expected_data}

        result = self.transfer_execution.create(
            mock.sentinel.transfer,
            shutdown_instances=mock.sentinel.shutdown_instances
        )

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            '/transfers/%s/executions' % mock.sentinel.transfer,
            expected_data, "execution")

    @mock.patch.object(transfer_executions.TransferExecutionManager, "_delete")
    def test_delete(self, mock_delete):
        result = self.transfer_execution.delete(
            mock.sentinel.transfer, mock.sentinel.execution)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            "/transfers/%s/executions/%s" % (mock.sentinel.transfer,
                                             mock.sentinel.execution))

    def test_cancel(self):
        result = self.transfer_execution.cancel(
            mock.sentinel.transfer, mock.sentinel.execution, force=False)

        self.assertEqual(
            self.transfer_execution.client.post.return_value,
            result
        )
        self.transfer_execution.client.post.assert_called_once_with(
            "/transfers/%s/executions/%s/actions" % (mock.sentinel.transfer,
                                                     mock.sentinel.execution),
            json={'cancel': {'force': False}})

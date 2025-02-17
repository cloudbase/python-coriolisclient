# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import os
from unittest import mock

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter
from coriolisclient.cli import transfer_executions
from coriolisclient.tests import test_base


class TransferExecutionFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Replic Execution Formatter."""

    def setUp(self):
        super(TransferExecutionFormatterTestCase, self).setUp()
        self.transfer = transfer_executions.TransferExecutionFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.created_at = "date1"
        obj2.created_at = "date2"
        obj3.created_at = "date3"
        obj_list = [obj2, obj1, obj3]

        result = self.transfer._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.action_id = mock.sentinel.action_id
        obj.id = mock.sentinel.id
        obj.status = mock.sentinel.status
        obj.created_at = mock.sentinel.created_at

        result = self.transfer._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.action_id,
                mock.sentinel.id,
                mock.sentinel.status,
                mock.sentinel.created_at
            ),
            result
        )


class TransferExecutionDetailFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Transfer Execution Detail Formatter."""

    def setUp(self):
        super(TransferExecutionDetailFormatterTestCase, self).setUp()
        self.transfer = transfer_executions.TransferExecutionDetailFormatter()

    def test_format_instances(self):
        obj = mock.Mock()
        task1 = mock.Mock()
        task1.instance = "mock_instance1"
        task2 = mock.Mock()
        task2.instance = "mock_instance2"
        obj.tasks = [task1, task2]
        expected_result = (
            'mock_instance1%(ls)smock_instance2'
            % {"ls": os.linesep}
        )

        result = self.transfer._format_instances(obj)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(formatter.EntityFormatter, '_format_progress_update')
    def test_format_progress_updates(self, mock_format_progress_update):
        update1 = {"created_at": "date2", "message2": "message2"}
        update2 = {"created_at": "date3", "message3": "message3"}
        update3 = {"index": 2, "created_at": "date1"}
        ret_update1 = "date2 [10] message2"
        ret_update2 = "date3 [20] message3"
        ret_update3 = "date1 [30] None"
        task_dict = {"progress_updates": [update3, update1, update2]}
        mock_format_progress_update.side_effect = [
            ret_update1, ret_update2, ret_update3]
        expected_result = (
            'date2 [10] message2%(ls)sdate3 [20] message3%(ls)s'
            'date1 [30] None' % {"ls": os.linesep}
        )

        result = self.transfer._format_progress_updates(task_dict)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(transfer_executions.TransferExecutionDetailFormatter,
                       '_format_progress_updates')
    def test_format_task(self, mock_format_progress_updates):
        mock_task = mock.Mock()
        task = {
            "depends_on": ["mock_dep1", "mock_dep2"],
            "id": mock.sentinel.id,
            "task_type": mock.sentinel.task_type,
            "instance": mock.sentinel.instance,
            "status": mock.sentinel.status,
            "exception_details": mock.sentinel.exception_details
        }
        mock_task.to_dict.return_value = task
        mock_format_progress_updates.return_value = (
            'date2 [10] message2%(ls)sdate3 [20] message3%(ls)s'
            'date1 [30] None' % {"ls": os.linesep}
        )
        expected_result = (
            'id: sentinel.id%(ls)s'
            'task_type: sentinel.task_type%(ls)s'
            'instance: sentinel.instance%(ls)s'
            'status: sentinel.status%(ls)s'
            'depends_on: mock_dep1, mock_dep2%(ls)s'
            'exception_details: sentinel.exception_details%(ls)s'
            'progress_updates:%(ls)s'
            'date2 [10] message2%(ls)s'
            'date3 [20] message3%(ls)s'
            'date1 [30] None' % {"ls": os.linesep})

        result = self.transfer._format_task(mock_task)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(transfer_executions.TransferExecutionDetailFormatter,
                       '_format_progress_updates')
    def test_format_task_no_progress_updates(
        self, mock_format_progress_updates):
        mock_task = mock.Mock()
        task = {
            "depends_on": ["mock_dep1", "mock_dep2"],
            "id": mock.sentinel.id,
            "task_type": mock.sentinel.task_type,
            "instance": mock.sentinel.instance,
            "status": mock.sentinel.status,
            "exception_details": mock.sentinel.exception_details
        }
        mock_task.to_dict.return_value = task
        mock_format_progress_updates.return_value = None
        expected_result = (
            'id: sentinel.id%(ls)s'
            'task_type: sentinel.task_type%(ls)s'
            'instance: sentinel.instance%(ls)s'
            'status: sentinel.status%(ls)s'
            'depends_on: mock_dep1, mock_dep2%(ls)s'
            'exception_details: sentinel.exception_details%(ls)s'
            'progress_updates:' % {"ls": os.linesep}
        )

        result = self.transfer._format_task(mock_task)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(transfer_executions.TransferExecutionDetailFormatter,
                       '_format_task')
    def test_format_tasks(self, mock_format_task):
        obj = mock.Mock()
        obj.tasks = [mock.sentinel.task1, mock.sentinel.task2]
        mock_format_task.side_effect = ["task1", "task2"]
        expected_result = 'task1%(ls)s%(ls)stask2' % {"ls": os.linesep}

        result = self.transfer._format_tasks(obj)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(transfer_executions.TransferExecutionDetailFormatter,
                       '_format_tasks')
    @mock.patch.object(transfer_executions.TransferExecutionDetailFormatter,
                       '_format_instances')
    def test_get_formatted_data(
        self,
        mock_format_instances,
        mock_format_tasks
    ):
        mock_obj = mock.Mock()
        obj = {
            "storage_mappings": {'default_storage': mock.sentinel.storage}
        }
        mock_obj.to_dict.return_value = obj
        mock_obj.id = mock.sentinel.id
        mock_obj.action_id = mock.sentinel.action_id
        mock_obj.status = mock.sentinel.status
        mock_obj.created_at = mock.sentinel.created_at
        mock_obj.updated_at = mock.sentinel.updated_at
        mock_format_instances.return_value = mock.sentinel.formatted_instances
        mock_format_tasks.return_value = mock.sentinel.formatted_tasks
        expected_result = (
            mock.sentinel.id,
            mock.sentinel.action_id,
            mock.sentinel.status,
            mock.sentinel.created_at,
            mock.sentinel.updated_at,
            mock.sentinel.formatted_instances,
            mock.sentinel.formatted_tasks,
        )

        result = self.transfer._get_formatted_data(mock_obj)

        self.assertEqual(
            expected_result,
            result
        )


class CreateTransferExecutionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Create Transfer Execution."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CreateTransferExecutionTestCase, self).setUp()
        self.transfer = transfer_executions.CreateTransferExecution(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfer_executions.TransferExecutionDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.transfer = mock.sentinel.transfer
        args.shutdown_instances = mock.sentinel.shutdown_instances
        args.auto_deploy = mock.sentinel.auto_deploy
        mock_execution = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_executions.create = \
            mock_execution

        result = self.transfer.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_execution.assert_called_once_with(
            mock.sentinel.transfer, mock.sentinel.shutdown_instances,
            mock.sentinel.auto_deploy)
        mock_get_formatted_entity.assert_called_once_with(
            mock_execution.return_value)


class ShowTransferExecutionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Show Transfer Execution."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ShowTransferExecutionTestCase, self).setUp()
        self.transfer = transfer_executions.ShowTransferExecution(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfer_executions.TransferExecutionDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.transfer = mock.sentinel.transfer
        args.id = mock.sentinel.id
        execution = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_executions.get = \
            execution

        result = self.transfer.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        execution.assert_called_once_with(args.transfer, args.id)
        mock_get_formatted_entity.assert_called_once_with(
            execution.return_value)


class CancelTransferExecutionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Cancel Transfer Execution."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CancelTransferExecutionTestCase, self).setUp()
        self.transfer = transfer_executions.CancelTransferExecution(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.transfer = mock.sentinel.transfer
        args.id = mock.sentinel.id
        args.force = False
        transfer_execution = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_executions = \
            transfer_execution

        self.transfer.take_action(args)

        transfer_execution.cancel.assert_called_once_with(
            mock.sentinel.transfer, mock.sentinel.id, False)


class DeleteTransferExecutionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Delete Transfer Execution."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeleteTransferExecutionTestCase, self).setUp()
        self.transfer = transfer_executions.DeleteTransferExecution(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.transfer = mock.sentinel.transfer
        args.id = mock.sentinel.id
        transfer_execution = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_executions = \
            transfer_execution

        self.transfer.take_action(args)

        transfer_execution.delete.assert_called_once_with(
            mock.sentinel.transfer, mock.sentinel.id)


class ListTransferExecutionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Transfer Execution."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListTransferExecutionTestCase, self).setUp()
        self.transfer = transfer_executions.ListTransferExecution(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfer_executions.TransferExecutionFormatter,
                       'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        args.transfer = mock.sentinel.transfer
        mock_transfer_list = mock.Mock()
        self.mock_app.client_manager.coriolis.transfer_executions.list = \
            mock_transfer_list

        result = self.transfer.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_transfer_list.assert_called_once_with(mock.sentinel.transfer)
        mock_list_objects.assert_called_once_with(
            mock_transfer_list.return_value)

# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import transfer_executions
from coriolisclient.cli import transfers
from coriolisclient.cli import utils as cli_utils
from coriolisclient.tests import test_base


class TransferFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Transfer Formatter."""

    def setUp(self):
        super(TransferFormatterTestCase, self).setUp()
        self.transfer = transfers.TransferFormatter()

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

    def test_format_last_execution(self):
        obj = mock.Mock()
        obj.executions = None

        result = self.transfer._format_last_execution(obj)

        self.assertEqual(
            "",
            result
        )

        execution1 = mock.Mock()
        execution2 = mock.Mock()
        execution3 = mock.Mock()
        execution1.created_at = "date1"
        execution2.created_at = "date2"
        execution3.created_at = "date3"
        execution1.to_dict.return_value = {
            "id": "mock_id1",
            "status": "mock_status1"
        }
        execution2.to_dict.return_value = {
            "id": "mock_id2",
            "status": "mock_status2"
        }
        execution3.to_dict.return_value = {
            "id": "mock_id3",
            "status": "mock_status3"
        }
        obj.executions = [execution1, execution3, execution2]

        result = self.transfer._format_last_execution(obj)

        self.assertEqual(
            "mock_id3 mock_status3",
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.last_execution_status = mock.sentinel.last_execution_status
        obj.instances = ["mock_instance3", "mock_instance1", "mock_instance2"]
        obj.notes = mock.sentinel.notes
        obj.scenario = mock.sentinel.scenario
        obj.created_at = mock.sentinel.created_at

        result = self.transfer._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.scenario,
                ('mock_instance3%(ls)smock_instance1%(ls)smock_instance2'
                 % {"ls": "\n"}),
                mock.sentinel.notes,
                mock.sentinel.last_execution_status,
                mock.sentinel.created_at
            ),
            result
        )


class TransferDetailFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Transfer Detail Formatter."""

    def setUp(self):
        super(TransferDetailFormatterTestCase, self).setUp()
        self.transfer = transfers.TransferDetailFormatter(
            show_instances_data=True)

    def test_format_instances(self):
        obj = mock.Mock()
        obj.instances = ["mock_instance3", "mock_instance1", "mock_instance2"]
        expected_result = (
            'mock_instance1%(ls)smock_instance2%(ls)smock_instance3'
            % {"ls": "\n"}
        )

        result = self.transfer._format_instances(obj)

        self.assertEqual(
            expected_result,
            result
        )

    def test_format_execution(self):
        execution = mock.Mock()
        execution.to_dict.return_value = {
            "id": "mock_id",
            "status": "mock_status"
        }
        expected_result = "mock_id mock_status"

        result = self.transfer._format_execution(execution)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(transfers.TransferDetailFormatter, '_format_execution')
    def test_format_executions(self, mock_format_execution):
        executions = mock.Mock()
        execution1 = mock.Mock()
        execution2 = mock.Mock()
        execution3 = mock.Mock()
        execution1.created_at = "date1"
        execution2.created_at = "date2"
        execution3.created_at = "date3"
        ret_execution1 = "mock_id1 mock_status1"
        ret_execution2 = "mock_id2 mock_status2"
        ret_execution3 = "mock_id3 mock_status3"
        mock_format_execution.side_effect = [
            ret_execution1, ret_execution2, ret_execution3]
        executions = [execution1, execution3, execution2]
        expected_result = (
            "mock_id1 mock_status1%(ls)s"
            "mock_id2 mock_status2%(ls)s"
            "mock_id3 mock_status3" % {"ls": "\n"}
        )

        result = self.transfer._format_executions(executions)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(transfers.TransferDetailFormatter, '_format_executions')
    @mock.patch.object(cli_utils, 'format_mapping')
    @mock.patch.object(cli_utils, 'format_json_for_object_property')
    @mock.patch.object(transfers.TransferDetailFormatter,
                       '_format_instances')
    @mock.patch.object(cli_utils, 'parse_storage_mappings')
    def test_get_formatted_data(
        self,
        mock_parse_storage_mappings,
        mock_format_instances,
        mock_format_json_for_object_property,
        mock_format_mapping,
        mock_format_executions
    ):
        mock_obj = mock.Mock()
        obj = {
            "storage_mappings": {'default_storage': mock.sentinel.storage}
        }
        mock_obj.to_dict.return_value = obj
        mock_obj.id = mock.sentinel.id
        mock_obj.created_at = mock.sentinel.created_at
        mock_obj.updated_at = mock.sentinel.updated_at
        mock_obj.reservation_id = mock.sentinel.reservation_id
        mock_format_instances.return_value = mock.sentinel.formatted_instances
        mock_obj.notes = mock.sentinel.notes
        mock_obj.origin_endpoint_id = mock.sentinel.origin_endpoint_id
        mock_obj.origin_minion_pool_id = mock.sentinel.origin_minion_pool_id
        mock_obj.destination_endpoint_id = \
            mock.sentinel.destination_endpoint_id
        mock_obj.destination_minion_pool_id = \
            mock.sentinel.destination_minion_pool_id
        mock_parse_storage_mappings.return_value = (
            mock.sentinel.default_storage,
            mock.sentinel.backend_mappings,
            mock.sentinel.disk_mappings
        )
        mock_format_json_for_object_property.side_effect = [
            mock.sentinel.instance_osmorphing_minion_pool_mappings,
            mock.sentinel.destination_environment,
            mock.sentinel.source_environment,
            mock.sentinel.network_map,
            mock.sentinel.user_scripts
        ]
        mock_format_mapping.side_effect = [
            mock.sentinel.disk_mapping, mock.sentinel.backend_mappings]
        mock_format_executions.return_value = \
            mock.sentinel.formatted_executions
        mock_obj.info = mock.sentinel.info
        mock_obj.scenario = mock.sentinel.scenario
        expected_result = [
            mock.sentinel.id,
            mock.sentinel.created_at,
            mock.sentinel.updated_at,
            mock.sentinel.scenario,
            mock.sentinel.reservation_id,
            mock.sentinel.formatted_instances,
            mock.sentinel.notes,
            mock.sentinel.origin_endpoint_id,
            mock.sentinel.origin_minion_pool_id,
            mock.sentinel.destination_endpoint_id,
            mock.sentinel.destination_minion_pool_id,
            mock.sentinel.instance_osmorphing_minion_pool_mappings,
            mock.sentinel.destination_environment,
            mock.sentinel.source_environment,
            mock.sentinel.network_map,
            mock.sentinel.disk_mapping,
            mock.sentinel.backend_mappings,
            mock.sentinel.default_storage,
            mock.sentinel.user_scripts,
            mock.sentinel.formatted_executions,
            mock.sentinel.info
        ]

        result = self.transfer._get_formatted_data(mock_obj)

        self.assertEqual(
            expected_result,
            result
        )


class CreateTransferTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Create Transfer."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CreateTransferTestCase, self).setUp()
        self.transfer = transfers.CreateTransfer(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(cli_utils, 'add_args_for_json_option_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        *_
    ):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(cli_utils, 'compose_user_scripts')
    @mock.patch.object(cli_utils, 'get_storage_mappings_dict_from_args')
    @mock.patch.object(cli_utils, 'get_option_value_from_args')
    @mock.patch.object(transfers.TransferDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity,
        mock_get_option_value_from_args,
        mock_get_storage_mappings_dict_from_args,
        mock_compose_user_scripts
    ):
        args = mock.Mock()
        args.instances = mock.sentinel.instances
        args.notes = mock.sentinel.notes
        args.scenario = mock.sentinel.scenario
        args.origin_minion_pool_id = mock.sentinel.origin_minion_pool_id
        args.destination_minion_pool_id = \
            mock.sentinel.destination_minion_pool_id
        args.instance_osmorphing_minion_pool_mappings = [
            {'instance_id': "instance_id1", 'pool_id': "pool_id1"},
            {'instance_id': "instance_id2", 'pool_id': "pool_id2"}
        ]
        mock_endpoints = mock.Mock()
        mock_transfers = mock.Mock()
        self.mock_app.client_manager.coriolis.endpoints = mock_endpoints
        mock_endpoints.get_endpoint_id_for_name.side_effect = [
            mock.sentinel.origin_endpoint_id,
            mock.sentinel.destination_endpoint_id
        ]
        self.mock_app.client_manager.coriolis.transfers.create = \
            mock_transfers
        mock_get_option_value_from_args.side_effect = [
            mock.sentinel.destination_environment,
            mock.sentinel.source_environment,
            mock.sentinel.network_map,
        ]

        result = self.transfer.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_transfers.assert_called_once_with(
            mock.sentinel.origin_endpoint_id,
            mock.sentinel.destination_endpoint_id,
            mock.sentinel.source_environment,
            mock.sentinel.destination_environment,
            mock.sentinel.instances,
            mock.sentinel.scenario,
            network_map=mock.sentinel.network_map,
            notes=mock.sentinel.notes,
            storage_mappings=(mock_get_storage_mappings_dict_from_args.
                              return_value),
            origin_minion_pool_id=mock.sentinel.origin_minion_pool_id,
            destination_minion_pool_id=
            mock.sentinel.destination_minion_pool_id,
            instance_osmorphing_minion_pool_mappings={
                'instance_id1': 'pool_id1', 'instance_id2': 'pool_id2'},
            user_scripts=mock_compose_user_scripts.return_value
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_transfers.return_value)


class ShowTransferTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Show Transfer."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ShowTransferTestCase, self).setUp()
        self.transfer = transfers.ShowTransfer(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfers.TransferDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(self, mock_get_formatted_entity):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_transfer = mock.Mock()
        self.mock_app.client_manager.coriolis.transfers.get = mock_transfer

        result = self.transfer.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_transfer.assert_called_once_with(mock.sentinel.id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_transfer.return_value)


class DeleteTransferTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Delete Transfer."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeleteTransferTestCase, self).setUp()
        self.transfer = transfers.DeleteTransfer(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_transfer = mock.Mock()
        self.mock_app.client_manager.coriolis.transfers.delete = mock_transfer

        self.transfer.take_action(args)

        mock_transfer.assert_called_once_with(mock.sentinel.id)


class DeleteTransferDisksTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Delete Transfer Disks."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeleteTransferDisksTestCase, self).setUp()
        self.transfer = transfers.DeleteTransferDisks(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfer_executions.TransferExecutionDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(self, mock_get_formatted_entity):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_transfer = mock.Mock()
        self.mock_app.client_manager.coriolis.transfers.delete_disks = \
            mock_transfer

        result = self.transfer.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_transfer.assert_called_once_with(mock.sentinel.id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_transfer.return_value)


class ListTransferTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Transfer."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListTransferTestCase, self).setUp()
        self.transfer = transfers.ListTransfer(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfers.TransferFormatter, 'list_objects')
    def test_take_action(self, mock_list_objects):
        args = mock.Mock()
        mock_transfer = mock.Mock()
        self.mock_app.client_manager.coriolis.transfers.list = mock_transfer

        result = self.transfer.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_list_objects.assert_called_once_with(mock_transfer.return_value)


class UpdateTransferTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Delete Transfer Disks."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(UpdateTransferTestCase, self).setUp()
        self.transfer = transfers.UpdateTransfer(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.transfer.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(transfer_executions.TransferExecutionDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(cli_utils, 'compose_user_scripts')
    @mock.patch.object(cli_utils, 'get_storage_mappings_dict_from_args')
    @mock.patch.object(cli_utils, 'get_option_value_from_args')
    def test_take_action(
        self,
        mock_get_option_value_from_args,
        mock_get_storage_mappings_dict_from_args,
        mock_compose_user_scripts,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.id = mock.sentinel.id
        args.global_scripts = mock.sentinel.global_scripts
        args.instance_scripts = mock.sentinel.instance_scripts
        args.notes = mock.sentinel.notes
        args.origin_minion_pool_id = mock.sentinel.origin_minion_pool_id
        args.destination_minion_pool_id = \
            mock.sentinel.destination_minion_pool_id
        args.instance_osmorphing_minion_pool_mappings = [
            {"instance_id": "mock_instance1", "pool_id": "mock_pool1"},
            {"instance_id": "mock_instance2", "pool_id": "mock_pool2"}
        ]
        mock_transfer = mock.Mock()
        self.mock_app.client_manager.coriolis.transfers = mock_transfer
        mock_get_option_value_from_args.side_effect = [
            mock.sentinel.destination_environment,
            mock.sentinel.source_environment,
            mock.sentinel.network_map
        ]
        mock_get_storage_mappings_dict_from_args.return_value = \
            mock.sentinel.storage_mappings
        mock_compose_user_scripts.return_value = mock.sentinel.user_scripts
        expected_updated_properties = {
            "destination_environment": mock.sentinel.destination_environment,
            "source_environment": mock.sentinel.source_environment,
            "storage_mappings": mock.sentinel.storage_mappings,
            "network_map": mock.sentinel.network_map,
            "notes": mock.sentinel.notes,
            "origin_minion_pool_id": mock.sentinel.origin_minion_pool_id,
            "destination_minion_pool_id":
            mock.sentinel.destination_minion_pool_id,
            "instance_osmorphing_minion_pool_mappings":
            {"mock_instance1": "mock_pool1", "mock_instance2": "mock_pool2"},
            "user_scripts": mock.sentinel.user_scripts
        }

        result = self.transfer.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_compose_user_scripts.assert_called_once_with(
            mock.sentinel.global_scripts, mock.sentinel.instance_scripts)
        mock_transfer.update.assert_called_once_with(
            mock.sentinel.id,
            expected_updated_properties
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_transfer.update.return_value)

    @mock.patch.object(cli_utils, 'compose_user_scripts')
    @mock.patch.object(cli_utils, 'get_storage_mappings_dict_from_args')
    @mock.patch.object(cli_utils, 'get_option_value_from_args')
    def test_take_action_no_updated_properties(
        self,
        mock_get_option_value_from_args,
        mock_get_storage_mappings_dict_from_args,
        mock_compose_user_scripts
    ):
        class CustomMock(mock.MagicMock):
            def __getattr__(self, name):
                return None
        args = CustomMock()
        args.global_scripts = mock.sentinel.global_scripts
        args.instance_scripts = mock.sentinel.instance_scripts
        mock_transfer = mock.Mock()
        self.mock_app.client_manager.coriolis.transfers = mock_transfer
        mock_get_option_value_from_args.return_value = None
        mock_get_storage_mappings_dict_from_args.return_value = None
        mock_compose_user_scripts.return_value = None

        self.assertRaises(
            ValueError,
            self.transfer.take_action,
            args
        )

        mock_compose_user_scripts.assert_called_once_with(
            mock.sentinel.global_scripts, mock.sentinel.instance_scripts)
        mock_transfer.update.assert_not_called()

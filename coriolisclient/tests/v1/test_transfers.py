# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import transfer_executions
from coriolisclient.v1 import transfers


class TransferTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Transfer."""

    @mock.patch.object(transfers.Transfer, "get")
    def test_properties(self, mock_get):
        mock_client = mock.Mock()
        self.transfer = transfers.Transfer(
            mock_client,
            {
                "source_environment": {
                    "source_environment1":
                        mock.sentinel.source_environment1,
                },
                "destination_environment": {
                    "destination_environment1":
                        mock.sentinel.destination_environment1,
                },
                "executions": [{"execution1": mock.sentinel.execution1},
                               {"execution2": mock.sentinel.execution2}],
            }
        )

        self.assertEqual(
            (
                mock.sentinel.source_environment1,
                mock.sentinel.destination_environment1,
                mock.sentinel.execution1,
                mock.sentinel.execution2
            ),
            (
                self.transfer.source_environment.source_environment1,
                self.transfer.destination_environment.destination_environment1,
                self.transfer.executions[0].execution1,
                self.transfer.executions[1].execution2,
            )
        )
        mock_get.assert_not_called()

    @mock.patch.object(transfers.Transfer, "get")
    def test_properties_none(self, mock_get):
        mock_client = mock.Mock()
        self.transfer = transfers.Transfer(
            mock_client,
            {}
        )

        self.assertEqual(
            (
                None,
                None,
                []
            ),
            (
                self.transfer.source_environment,
                self.transfer.destination_environment,
                self.transfer.executions
            )
        )
        mock_get.assert_called_once()


class TransferManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Transfer Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(TransferManagerTestCase, self).setUp()
        self.transfer = transfers.TransferManager(mock_client)

    @mock.patch.object(transfers.TransferManager, "_list")
    def test_list(self, mock_list):
        result = self.transfer.list(detail=False)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with("/transfers", "transfers")

    @mock.patch.object(transfers.TransferManager, "_list")
    def test_list_details(self, mock_list):
        result = self.transfer.list(detail=True)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with("/transfers/detail", "transfers")

    @mock.patch.object(transfers.TransferManager, "_get")
    def test_get(self, mock_get):
        result = self.transfer.get(mock.sentinel.transfer)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            "/transfers/%s" % mock.sentinel.transfer, "transfer")

    @mock.patch.object(transfers.TransferManager, "_post")
    def test_create(self, mock_post):
        expected_data = {
            "origin_endpoint_id": mock.sentinel.origin_endpoint_id,
            "destination_endpoint_id": mock.sentinel.destination_endpoint_id,
            "source_environment": mock.sentinel.source_environment,
            "destination_environment": {
                "network_map": mock.sentinel.network_map,
                "storage_mappings": mock.sentinel.storage_mappings
            },
            "instances": mock.sentinel.instances,
            "scenario": mock.sentinel.scenario,
            "network_map": mock.sentinel.network_map,
            "notes": mock.sentinel.notes,
            "storage_mappings": mock.sentinel.storage_mappings,
            "user_scripts": mock.sentinel.user_scripts,
            "origin_minion_pool_id": mock.sentinel.origin_minion_pool_id,
            "destination_minion_pool_id":
                mock.sentinel.destination_minion_pool_id,
            "instance_osmorphing_minion_pool_mappings":
                mock.sentinel.instance_osmorphing_minion_pool_mappings,
            "clone_disks": True,
            "skip_os_morphing": False,
        }
        expected_data = {"transfer": expected_data}

        result = self.transfer.create(
            mock.sentinel.origin_endpoint_id,
            mock.sentinel.destination_endpoint_id,
            mock.sentinel.source_environment,
            {
                "network_map": mock.sentinel.network_map,
                "storage_mappings": mock.sentinel.storage_mappings
            },
            mock.sentinel.instances,
            mock.sentinel.scenario,
            network_map=None,
            notes=mock.sentinel.notes,
            storage_mappings=None,
            user_scripts=mock.sentinel.user_scripts,
            origin_minion_pool_id=mock.sentinel.origin_minion_pool_id,
            destination_minion_pool_id=
            mock.sentinel.destination_minion_pool_id,
            instance_osmorphing_minion_pool_mappings=
            mock.sentinel.instance_osmorphing_minion_pool_mappings,
            clone_disks=True,
            skip_os_morphing=False,
        )

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            "/transfers", expected_data, "transfer")

    @mock.patch.object(transfers.TransferManager, "_delete")
    def test_delete(self, mock_delete):
        result = self.transfer.delete(mock.sentinel.transfer)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            "/transfers/%s" % mock.sentinel.transfer)

    @mock.patch.object(transfer_executions, "TransferExecution")
    def test_delete_disks(self, mock_TransferExecution):
        result = self.transfer.delete_disks(mock.sentinel.transfer)

        self.assertEqual(
            mock_TransferExecution.return_value,
            result
        )
        self.transfer.client.post.assert_called_once_with(
            "/transfers/%s/actions" % mock.sentinel.transfer,
            json={'delete-disks': None})
        mock_TransferExecution.assert_called_once_with(
            self.transfer,
            (self.transfer.client.post.return_value.json.return_value.
             get("execution")),
            loaded=True
        )

    @mock.patch.object(transfer_executions, "TransferExecution")
    def test_update(self, mock_TransferExecution):
        updated_values = {"network_map": mock.sentinel.network_map}
        result = self.transfer.update(mock.sentinel.transfer, updated_values)

        self.assertEqual(
            mock_TransferExecution.return_value,
            result
        )
        self.transfer.client.put.assert_called_once_with(
            "/transfers/%s" % mock.sentinel.transfer,
            json={"transfer": updated_values})
        mock_TransferExecution.assert_called_once_with(
            self.transfer,
            (self.transfer.client.put.return_value.json.return_value.
             get("execution")),
            loaded=True
        )

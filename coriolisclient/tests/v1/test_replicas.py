# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import replica_executions
from coriolisclient.v1 import replicas


class ReplicaTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Replica."""

    @mock.patch.object(replicas.Replica, "get")
    def test_properties(self, mock_get):
        mock_client = mock.Mock()
        self.replica = replicas.Replica(
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
                self.replica.source_environment.source_environment1,
                self.replica.destination_environment.destination_environment1,
                self.replica.executions[0].execution1,
                self.replica.executions[1].execution2,
            )
        )
        mock_get.assert_not_called()

    @mock.patch.object(replicas.Replica, "get")
    def test_properties_none(self, mock_get):
        mock_client = mock.Mock()
        self.replica = replicas.Replica(
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
                self.replica.source_environment,
                self.replica.destination_environment,
                self.replica.executions
            )
        )
        mock_get.assert_called_once()


class ReplicaManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Replica Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(ReplicaManagerTestCase, self).setUp()
        self.replica = replicas.ReplicaManager(mock_client)

    @mock.patch.object(replicas.ReplicaManager, "_list")
    def test_list(self, mock_list):
        result = self.replica.list(detail=False)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with("/replicas", "replicas")

    @mock.patch.object(replicas.ReplicaManager, "_list")
    def test_list_details(self, mock_list):
        result = self.replica.list(detail=True)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with("/replicas/detail", "replicas")

    @mock.patch.object(replicas.ReplicaManager, "_get")
    def test_get(self, mock_get):
        result = self.replica.get(mock.sentinel.replica)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            "/replicas/%s" % (mock.sentinel.replica), "replica")

    @mock.patch.object(replicas.ReplicaManager, "_post")
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
            "network_map": mock.sentinel.network_map,
            "notes": mock.sentinel.notes,
            "storage_mappings": mock.sentinel.storage_mappings,
            "user_scripts": mock.sentinel.user_scripts,
            "origin_minion_pool_id": mock.sentinel.origin_minion_pool_id,
            "destination_minion_pool_id":
                mock.sentinel.destination_minion_pool_id,
            "instance_osmorphing_minion_pool_mappings":
                mock.sentinel.instance_osmorphing_minion_pool_mappings,
        }
        expected_data = {"replica": expected_data}

        result = self.replica.create(
            mock.sentinel.origin_endpoint_id,
            mock.sentinel.destination_endpoint_id,
            mock.sentinel.source_environment,
            {
                "network_map": mock.sentinel.network_map,
                "storage_mappings": mock.sentinel.storage_mappings
            },
            mock.sentinel.instances,
            network_map=None,
            notes=mock.sentinel.notes,
            storage_mappings=None,
            user_scripts=mock.sentinel.user_scripts,
            origin_minion_pool_id=mock.sentinel.origin_minion_pool_id,
            destination_minion_pool_id=
            mock.sentinel.destination_minion_pool_id,
            instance_osmorphing_minion_pool_mappings=
            mock.sentinel.instance_osmorphing_minion_pool_mappings,
        )

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            "/replicas", expected_data, "replica")

    @mock.patch.object(replicas.ReplicaManager, "_delete")
    def test_delete(self, mock_delete):
        result = self.replica.delete(mock.sentinel.replica)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            "/replicas/%s" % mock.sentinel.replica)

    @mock.patch.object(replica_executions, "ReplicaExecution")
    def test_delete_disks(self, mock_ReplicaExecution):
        result = self.replica.delete_disks(mock.sentinel.replica)

        self.assertEqual(
            mock_ReplicaExecution.return_value,
            result
        )
        self.replica.client.post.assert_called_once_with(
            "/replicas/%s/actions" % mock.sentinel.replica,
            json={'delete-disks': None})
        mock_ReplicaExecution.assert_called_once_with(
            self.replica,
            (self.replica.client.post.return_value.json.return_value.
             get("execution")),
            loaded=True
        )

    @mock.patch.object(replica_executions, "ReplicaExecution")
    def test_update(self, mock_ReplicaExecution):
        updated_values = {"network_map": mock.sentinel.network_map}
        result = self.replica.update(mock.sentinel.replica, updated_values)

        self.assertEqual(
            mock_ReplicaExecution.return_value,
            result
        )
        self.replica.client.put.assert_called_once_with(
            "/replicas/%s" % mock.sentinel.replica,
            json={"replica": updated_values})
        mock_ReplicaExecution.assert_called_once_with(
            self.replica,
            (self.replica.client.put.return_value.json.return_value.
             get("execution")),
            loaded=True
        )

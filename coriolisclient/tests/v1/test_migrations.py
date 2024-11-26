# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import migrations


class MigrationTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Migration."""

    def test_properties(self):
        mock_client = mock.Mock()
        self.migration = migrations.Migration(
            mock_client,
            {
                "source_environment": {
                    "source_environment1": mock.sentinel.source_environment},
                "destination_environment": {
                    "destination_environment1":
                        mock.sentinel.destination_environment},
                "transfer_result": {
                    "transfer_result1": mock.sentinel.transfer_result},
                "tasks": [{"task1": mock.sentinel.task1},
                          {"task2": mock.sentinel.task2}]
            }
        )
        self.assertEqual(
            (
                mock.sentinel.source_environment,
                mock.sentinel.destination_environment,
                mock.sentinel.transfer_result,
                mock.sentinel.task1,
                mock.sentinel.task2
            ),
            (
                self.migration.source_environment.source_environment1,
                (self.migration.destination_environment.
                 destination_environment1),
                self.migration.transfer_result.transfer_result1,
                self.migration.tasks[0].task1,
                self.migration.tasks[1].task2
            )
        )

    @mock.patch.object(migrations.Migration, "get")
    def test_properties_none(self, mock_get):
        mock_client = mock.Mock()
        self.migration = migrations.Migration(
            mock_client,
            {}
        )
        self.assertEqual(
            (
                None,
                None,
                None,
                []
            ),
            (
                self.migration.source_environment,
                self.migration.destination_environment,
                self.migration.transfer_result,
                self.migration.tasks,
            )
        )
        mock_get.assert_called_once()


class MigrationManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Migration Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(MigrationManagerTestCase, self).setUp()
        self.migration = migrations.MigrationManager(mock_client)

    @mock.patch.object(migrations.MigrationManager, "_list")
    def test_list(self, mock_list):
        result = self.migration.list(detail=True)

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with("/migrations/detail", "migrations")

    @mock.patch.object(migrations.MigrationManager, "_get")
    def test_get(self, mock_get):
        result = self.migration.get(mock.sentinel.migration)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            "/migrations/sentinel.migration", "migration")

    @mock.patch.object(migrations.MigrationManager, "_post")
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
            "skip_os_morphing": False,
            "replication_count": mock.sentinel.replication_count,
            "shutdown_instances": mock.sentinel.shutdown_instances,
            "user_scripts": mock.sentinel.user_scripts,
            "origin_minion_pool_id": mock.sentinel.origin_minion_pool_id,
            "destination_minion_pool_id":
                mock.sentinel.destination_minion_pool_id,
            "instance_osmorphing_minion_pool_mappings":
                mock.sentinel.instance_osmorphing_minion_pool_mappings,
        }
        expected_data = {"migration": expected_data}

        result = self.migration.create(
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
            skip_os_morphing=False,
            replication_count=mock.sentinel.replication_count,
            shutdown_instances=mock.sentinel.shutdown_instances,
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
            "/migrations", expected_data, "migration")

    @mock.patch.object(migrations.MigrationManager, "_post")
    def test_create_from_replica(self, mock_post):
        expected_data = {
            "replica_id": mock.sentinel.replica_id,
            "clone_disks": False,
            "force": False,
            "skip_os_morphing": False,
            "user_scripts": mock.sentinel.user_scripts,
            "instance_osmorphing_minion_pool_mappings":
                mock.sentinel.instance_osmorphing_minion_pool_mappings,
        }
        expected_data = {"migration": expected_data}

        result = self.migration.create_from_replica(
            mock.sentinel.replica_id,
            clone_disks=False,
            force=False,
            skip_os_morphing=False,
            user_scripts=mock.sentinel.user_scripts,
            instance_osmorphing_minion_pool_mappings=
            mock.sentinel.instance_osmorphing_minion_pool_mappings,
        )

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            "/migrations", expected_data, "migration")

    @mock.patch.object(migrations.MigrationManager, "_delete")
    def test_delete(self, mock_delete):
        result = self.migration.delete(mock.sentinel.migration)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            "/migrations/%s" % mock.sentinel.migration)

    def test_cancel(self):
        result = self.migration.cancel(mock.sentinel.migration, force=False)

        self.assertEqual(
            self.migration.client.post.return_value,
            result
        )
        self.migration.client.post.assert_called_once_with(
            "/migrations/%s/actions" % mock.sentinel.migration,
            json={'cancel': {'force': False}})

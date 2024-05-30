# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import minion_pools


class MinionPoolManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Migration Pool Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(MinionPoolManagerTestCase, self).setUp()
        self.minion_pool = minion_pools.MinionPoolManager(mock_client)

    @mock.patch.object(minion_pools.MinionPoolManager, "_list")
    def test_list(self, mock_list):
        result = self.minion_pool.list()

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            "/minion_pools", response_key="minion_pools")

    @mock.patch.object(minion_pools.MinionPoolManager, "_get")
    def test_get(self, mock_get):
        result = self.minion_pool.get(mock.sentinel.minion_pool)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            "/minion_pools/sentinel.minion_pool", response_key="minion_pool")

    @mock.patch.object(minion_pools.MinionPoolManager, "_post")
    def test_create(self, mock_post):
        expected_data = {
            "name": mock.sentinel.name,
            "endpoint_id": mock.sentinel.endpoint,
            "platform": mock.sentinel.platform,
            "os_type": mock.sentinel.os_type,
            "environment_options": mock.sentinel.environment_options,
            "minimum_minions": mock.sentinel.minimum_minions,
            "maximum_minions": mock.sentinel.maximum_minions,
            "minion_max_idle_time": mock.sentinel.minion_max_idle_time,
            "minion_retention_strategy":
                mock.sentinel.minion_retention_strategy,
            "notes": mock.sentinel.notes,
            "skip_allocation": False,
        }
        expected_data = {"minion_pool": expected_data}

        result = self.minion_pool.create(
            mock.sentinel.name,
            mock.sentinel.endpoint,
            mock.sentinel.platform,
            mock.sentinel.os_type,
            environment_options=mock.sentinel.environment_options,
            minimum_minions=mock.sentinel.minimum_minions,
            maximum_minions=mock.sentinel.maximum_minions,
            minion_max_idle_time=mock.sentinel.minion_max_idle_time,
            minion_retention_strategy=mock.sentinel.minion_retention_strategy,
            notes=mock.sentinel.notes,
            skip_allocation=False,
        )

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            "/minion_pools", expected_data, response_key="minion_pool")

    @mock.patch.object(minion_pools.MinionPoolManager, "_put")
    def test_update(self, mock_put):
        result = self.minion_pool.update(
            mock.sentinel.minion_pool, mock.sentinel.updated_values)

        self.assertEqual(
            mock_put.return_value,
            result
        )
        mock_put.assert_called_once_with(
            "/minion_pools/%s" % mock.sentinel.minion_pool,
            {"minion_pool": mock.sentinel.updated_values}, 'minion_pool')

    @mock.patch.object(minion_pools.MinionPoolManager, "_delete")
    def test_delete(self, mock_delete):
        result = self.minion_pool.delete(mock.sentinel.minion_pool)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            "/minion_pools/%s" % mock.sentinel.minion_pool)

    @mock.patch.object(minion_pools.MinionPoolManager, "_post")
    def test_allocate_minion_pool(self, mock_post):
        result = self.minion_pool.allocate_minion_pool(
            mock.sentinel.minion_pool)

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            "/minion_pools/%s/actions" % mock.sentinel.minion_pool,
            {'allocate': None}, response_key='minion_pool')

    @mock.patch.object(minion_pools.MinionPoolManager, "_post")
    def test_refresh_minion_pool(self, mock_post):
        result = self.minion_pool.refresh_minion_pool(
            mock.sentinel.minion_pool)

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            "/minion_pools/%s/actions" % mock.sentinel.minion_pool,
            {'refresh': None}, response_key='minion_pool')

    @mock.patch.object(minion_pools.MinionPoolManager, "_post")
    def test_deallocate_minion_pool(self, mock_post):
        result = self.minion_pool.deallocate_minion_pool(
            mock.sentinel.minion_pool, force=False)

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            "/minion_pools/%s/actions" % mock.sentinel.minion_pool,
            {'deallocate': {'force': False}},
            response_key='minion_pool')

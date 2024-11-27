# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import endpoint_storage


class EndpointStorageManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Endpoint Storage Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(EndpointStorageManagerTestCase, self).setUp()
        self.endpoint = endpoint_storage.EndpointStorageManager(mock_client)

    @mock.patch.object(endpoint_storage.EndpointStorageManager, '_list')
    def test_list(
        self,
        mock_list
    ):
        mock_endpoint = mock.Mock()
        mock_endpoint.uuid = '53773ab8-1474-4cf7-bf0c-a496a6595ecb'

        result = self.endpoint.list(
            mock_endpoint,
            environment={"env": "mock_env"}
        )

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            ('/endpoints/53773ab8-1474-4cf7-bf0c-a496a6595ecb/storage'
             '?env=eyJlbnYiOiAibW9ja19lbnYifQ=='),
            'storage',
            values_key='storage_backends')

    @mock.patch.object(endpoint_storage.EndpointStorageManager, '_get')
    def test_get_default(
        self,
        mock_get
    ):
        mock_endpoint = mock.Mock()
        mock_endpoint.uuid = '53773ab8-1474-4cf7-bf0c-a496a6595ecb'
        mock_get.return_value = {"config_default": "mock_default"}

        result = self.endpoint.get_default(
            mock_endpoint,
            environment={"env": "mock_env"},
        )

        self.assertEqual(
            "mock_default",
            result
        )
        mock_get.assert_called_once_with(
            ('/endpoints/53773ab8-1474-4cf7-bf0c-a496a6595ecb/storage'
             '?env=eyJlbnYiOiAibW9ja19lbnYifQ=='),
            'storage')

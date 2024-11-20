# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient import base
from coriolisclient.tests import test_base
from coriolisclient.v1 import common
from coriolisclient.v1 import endpoint_storage


class EndpointStorageManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Endpoint Storage Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(EndpointStorageManagerTestCase, self).setUp()
        self.endpoint = endpoint_storage.EndpointStorageManager(mock_client)

    @mock.patch.object(endpoint_storage.EndpointStorageManager, '_list')
    @mock.patch.object(common, 'encode_base64_param')
    @mock.patch.object(base, 'getid')
    def test_list(
        self,
        mock_getid,
        mock_encode_base64_param,
        mock_list
    ):
        mock_endpoint = mock.Mock()
        mock_getid.return_value = mock.sentinel.id
        mock_encode_base64_param.return_value = mock.sentinel.encoded_env

        result = self.endpoint.list(
            mock_endpoint,
            mock.sentinel.environment,
        )

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            ('/endpoints/sentinel.id/storage'
             '?env=sentinel.encoded_env'),
            'storage',
            values_key='storage_backends')

    @mock.patch.object(endpoint_storage.EndpointStorageManager, '_get')
    @mock.patch.object(common, 'encode_base64_param')
    @mock.patch.object(base, 'getid')
    def test_get_default(
        self,
        mock_getid,
        mock_encode_base64_param,
        mock_get
    ):
        mock_endpoint = mock.Mock()
        mock_getid.return_value = mock.sentinel.id
        mock_encode_base64_param.return_value = mock.sentinel.encoded_env
        mock_get.return_value = {
            "config_default": mock.sentinel.config_default}

        result = self.endpoint.get_default(
            mock_endpoint,
            mock.sentinel.environment,
        )

        self.assertEqual(
            mock.sentinel.config_default,
            result
        )
        mock_get.assert_called_once_with(
            ('/endpoints/sentinel.id/storage'
             '?env=sentinel.encoded_env'),
            'storage')

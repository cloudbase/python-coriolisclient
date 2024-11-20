# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient import base
from coriolisclient.tests import test_base
from coriolisclient.v1 import common
from coriolisclient.v1 import endpoint_networks


class EndpointNetworkManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Endpoint Network Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(EndpointNetworkManagerTestCase, self).setUp()
        self.endpoint = endpoint_networks.EndpointNetworkManager(mock_client)

    @mock.patch.object(endpoint_networks.EndpointNetworkManager, '_list')
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
            ('/endpoints/sentinel.id/networks'
             '?env=sentinel.encoded_env'),
            'networks')

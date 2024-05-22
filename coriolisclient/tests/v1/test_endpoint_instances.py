# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import common
from coriolisclient.v1 import endpoint_instances


class EndpointInstanceTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Endpoint Instance."""

    def setUp(self):
        mock_client = mock.Mock()
        super(EndpointInstanceTestCase, self).setUp()
        self.endpoint = endpoint_instances.EndpointInstance(
            mock_client,
            {"flavor_name": mock.sentinel.flavor_name})

    def test_flavor_name(self):
        result = self.endpoint.flavor_name

        self.assertEqual(
            mock.sentinel.flavor_name,
            result
        )


class EndpointInstanceManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Endpoint Instance Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(EndpointInstanceManagerTestCase, self).setUp()
        self.endpoint = endpoint_instances.EndpointInstanceManager(mock_client)

    @mock.patch.object(endpoint_instances.EndpointInstanceManager, '_list')
    def test_list(
        self,
        mock_list
    ):
        mock_endpoint = mock.Mock()
        mock_endpoint.uuid = '53773ab8-1474-4cf7-bf0c-a496a6595ecb'

        result = self.endpoint.list(
            mock_endpoint,
            env={"env": "mock_env"},
            marker="mock_marker",
            limit="mock_limit",
            name="mock_name"
        )

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            ('/endpoints/53773ab8-1474-4cf7-bf0c-a496a6595ecb/instances'
             '?marker=mock_marker&limit=mock_limit&name=mock_name&'
             'env=eyJlbnYiOiAibW9ja19lbnYifQ%3D%3D'),
            'instances')

    @mock.patch.object(common, 'encode_base64_param')
    def test_list_value_error(
        self,
        mock_encode_base64_param
    ):
        mock_endpoint = mock.Mock()
        mock_encode_base64_param.return_value = mock.sentinel.encoded_env

        self.assertRaises(
            ValueError,
            self.endpoint.list,
            mock_endpoint,
            env=mock.sentinel.env
        )

        mock_encode_base64_param.assert_not_called()

    @mock.patch.object(endpoint_instances.EndpointInstanceManager, '_get')
    def test_get(
        self,
        mock_get
    ):
        mock_endpoint = mock.Mock()
        mock_endpoint.uuid = '53773ab8-1474-4cf7-bf0c-a496a6595ecb'

        result = self.endpoint.get(
            mock_endpoint,
            "mock_id",
            env={"env": "mock_env"},
        )

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            ('/endpoints/53773ab8-1474-4cf7-bf0c-a496a6595ecb/instances/'
             'bW9ja19pZA==?env=eyJlbnYiOiAibW9ja19lbnYifQ=='),
            'instance')

    def test_get_value_error(self):
        mock_endpoint = mock.Mock()

        self.assertRaises(
            ValueError,
            self.endpoint.get,
            mock_endpoint,
            "mock_instance_id",
            env=mock.sentinel.env
        )

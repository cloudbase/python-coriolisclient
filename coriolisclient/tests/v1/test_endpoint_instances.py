# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from six.moves.urllib import parse as urlparse
from unittest import mock

from coriolisclient import base
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
    @mock.patch.object(urlparse, 'urlencode')
    @mock.patch.object(common, 'encode_base64_param')
    @mock.patch.object(base, 'getid')
    def test_list(
        self,
        mock_getid,
        mock_encode_base64_param,
        mock_urlencode,
        mock_list
    ):
        mock_endpoint = mock.Mock()
        mock_getid.return_value = mock.sentinel.id
        mock_encode_base64_param.return_value = mock.sentinel.encoded_env
        mock_urlencode.return_value = "mock_url_query"

        result = self.endpoint.list(
            mock_endpoint,
            env={"env": mock.sentinel.env},
            marker=mock.sentinel.marker,
            limit=mock.sentinel.limit,
            name=mock.sentinel.name
        )

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_getid.assert_called_once_with(mock_endpoint)
        mock_encode_base64_param.assert_called_once_with(
            {"env": mock.sentinel.env}, is_json=True)
        mock_urlencode.assert_called_once_with(
            {
                "marker": mock.sentinel.marker,
                "limit": mock.sentinel.limit,
                "name": mock.sentinel.name,
                "env": mock_encode_base64_param.return_value
            }
        )
        mock_list.assert_called_once_with(
            ('/endpoints/sentinel.id/instances'
             '?mock_url_query'),
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
    @mock.patch.object(common, 'encode_base64_param')
    @mock.patch.object(base, 'getid')
    def test_get(
        self,
        mock_getid,
        mock_encode_base64_param,
        mock_get
    ):
        mock_endpoint = mock.Mock()
        mock_getid.return_value = mock.sentinel.id
        mock_encode_base64_param.side_effect = [
            mock.sentinel.encoded_id, mock.sentinel.encoded_env]

        result = self.endpoint.get(
            mock_endpoint,
            mock.sentinel.instance_id,
            env={"env": mock.sentinel.env}
        )

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_getid.assert_called_once_with(mock_endpoint)
        mock_encode_base64_param.assert_has_calls([
            mock.call(mock.sentinel.instance_id),
            mock.call({"env": mock.sentinel.env}, is_json=True)
        ])
        mock_get.assert_called_once_with(
            ('/endpoints/sentinel.id/instances/sentinel.encoded_id'
             '?env=sentinel.encoded_env'),
            'instance')

    @mock.patch.object(common, 'encode_base64_param')
    def test_get_value_error(
        self,
        mock_encode_base64_param
    ):
        mock_endpoint = mock.Mock()
        mock_encode_base64_param.return_value = mock.sentinel.encoded_env

        self.assertRaises(
            ValueError,
            self.endpoint.get,
            mock_endpoint,
            mock.sentinel.instance_id,
            env=mock.sentinel.env
        )

        mock_encode_base64_param.assert_called_once_with(
            mock.sentinel.instance_id)

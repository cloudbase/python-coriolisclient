# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient import exceptions
from coriolisclient.tests import test_base
from coriolisclient.v1 import endpoints


class EndpointTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Endpoint."""

    def setUp(self):
        super(EndpointTestCase, self).setUp()
        self.endpoint = endpoints.Endpoint(
            None,
            {
                "connection_info": {
                    "connection_info1": mock.sentinel.connection_info}
            }
        )

    def test_connection_info(self):
        result = self.endpoint.connection_info

        self.assertEqual(
            mock.sentinel.connection_info,
            result.connection_info1
        )


class EndpointManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Endpoint Manager."""

    def setUp(self):
        self.mock_client = mock.Mock()
        super(EndpointManagerTestCase, self).setUp()
        self.endpoint = endpoints.EndpointManager(self.mock_client)

    @mock.patch.object(endpoints.EndpointManager, '_list')
    def test_list(
        self,
        mock_list
    ):
        result = self.endpoint.list()

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with('/endpoints', 'endpoints')

    @mock.patch.object(endpoints.EndpointManager, '_get')
    def test_get(
        self,
        mock_get
    ):
        mock_endpoint = mock.Mock()
        mock_endpoint.uuid = '53773ab8-1474-4cf7-bf0c-a496a6595ecb'

        result = self.endpoint.get(mock_endpoint)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            '/endpoints/53773ab8-1474-4cf7-bf0c-a496a6595ecb', 'endpoint')

    @mock.patch.object(endpoints.EndpointManager, '_post')
    def test_create(
        self,
        mock_post
    ):
        result = self.endpoint.create(
            mock.sentinel.name,
            mock.sentinel.endpoint_type,
            mock.sentinel.connection_info,
            mock.sentinel.description,
            mock.sentinel.regions
        )
        expected_data = {
            "endpoint": {
                "name": mock.sentinel.name,
                "type": mock.sentinel.endpoint_type,
                "description": mock.sentinel.description,
                "connection_info": mock.sentinel.connection_info,
                "mapped_regions": mock.sentinel.regions
            }
        }

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            '/endpoints', expected_data, 'endpoint')

    @mock.patch.object(endpoints.EndpointManager, '_put')
    def test_update(
        self,
        mock_put
    ):
        mock_endpoint = mock.Mock()
        mock_endpoint.uuid = '53773ab8-1474-4cf7-bf0c-a496a6595ecb'

        result = self.endpoint.update(
            mock_endpoint,
            mock.sentinel.updated_values
        )
        expected_data = {
            "endpoint": mock.sentinel.updated_values
        }

        self.assertEqual(
            mock_put.return_value,
            result
        )
        mock_put.assert_called_once_with(
            '/endpoints/53773ab8-1474-4cf7-bf0c-a496a6595ecb',
            expected_data, 'endpoint')

    @mock.patch.object(endpoints.EndpointManager, '_delete')
    def test_delete(
        self,
        mock_delete
    ):
        mock_endpoint = mock.Mock()
        mock_endpoint.uuid = '53773ab8-1474-4cf7-bf0c-a496a6595ecb'

        result = self.endpoint.delete(mock_endpoint)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            '/endpoints/53773ab8-1474-4cf7-bf0c-a496a6595ecb')

    def test_validate_connection(self):
        mock_endpoint = mock.Mock()
        mock_endpoint.uuid = '53773ab8-1474-4cf7-bf0c-a496a6595ecb'
        self.mock_client.post.return_value.json.return_value = {
            "validate-connection": {
                "valid": mock.sentinel.valid,
                "message": mock.sentinel.message
            }
        }

        result = self.endpoint.validate_connection(mock_endpoint)

        self.assertEqual(
            (mock.sentinel.valid, mock.sentinel.message),
            result
        )
        self.mock_client.post.assert_called_once_with(
            '/endpoints/53773ab8-1474-4cf7-bf0c-a496a6595ecb/actions',
            json={'validate-connection': None})

    @mock.patch.object(endpoints.EndpointManager, '_get_endpoint_id_for_name')
    def test_get_endpoint_id_for_name_uuid(
        self,
        mock_get_endpoint_id_for_name
    ):
        mock_endpoint = '53773ab8-1474-4cf7-bf0c-a496a6595ecb'
        result = self.endpoint.get_endpoint_id_for_name(mock_endpoint)

        self.assertEqual(
            '53773ab8-1474-4cf7-bf0c-a496a6595ecb',
            result
        )
        mock_get_endpoint_id_for_name.assert_not_called()

    @mock.patch.object(endpoints.EndpointManager, '_get_endpoint_id_for_name')
    def test_get_endpoint_id_for_name(
        self,
        mock_get_endpoint_id_for_name
    ):
        mock_endpoint = mock.Mock()

        result = self.endpoint.get_endpoint_id_for_name(mock_endpoint)

        self.assertEqual(
            mock_get_endpoint_id_for_name.return_value,
            result
        )

    @mock.patch.object(endpoints.EndpointManager, 'list')
    def test__get_endpoint_id_for_name(
        self,
        mock_list
    ):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.id = '1'
        obj2.id = '2'
        obj3.id = '3'
        obj1.name = 'mock_name1'
        obj2.name = 'mock_name2'
        obj3.name = 'mock_name3'
        obj_list = [obj1, obj2, obj3]
        mock_list.return_value = obj_list
        endpoint_name = "mock_name2"

        result = self.endpoint._get_endpoint_id_for_name(endpoint_name)

        self.assertEqual(
            '2',
            result
        )

    @mock.patch.object(endpoints.EndpointManager, 'list')
    def test__get_endpoint_id_for_name_not_found(
        self,
        mock_list
    ):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.id = '1'
        obj2.id = '2'
        obj3.id = '3'
        obj1.name = 'mock_name1'
        obj2.name = 'mock_name2'
        obj3.name = 'mock_name3'
        obj_list = [obj1, obj2, obj3]
        mock_list.return_value = obj_list
        endpoint_name = "mock_name4"

        self.assertRaises(
            exceptions.EndpointIDNotFound,
            self.endpoint._get_endpoint_id_for_name,
            endpoint_name
        )

    @mock.patch.object(endpoints.EndpointManager, 'list')
    def test__get_endpoint_id_for_name_not_unique(
        self,
        mock_list
    ):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.id = '1'
        obj2.id = '2'
        obj3.id = '3'
        obj1.name = 'mock_name1'
        obj2.name = 'mock_name2'
        obj3.name = 'mock_name2'
        obj_list = [obj1, obj2, obj3]
        mock_list.return_value = obj_list
        endpoint_name = "mock_name2"

        self.assertRaises(
            exceptions.NoUniqueEndpointNameMatch,
            self.endpoint._get_endpoint_id_for_name,
            endpoint_name
        )

# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from cliff import lister
from unittest import mock

from coriolisclient.cli import endpoint_storage
from coriolisclient.cli import utils as cli_utils
from coriolisclient.tests import test_base


class EndpointStorageFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Endpoint Storage Formatter."""

    def setUp(self):
        super(EndpointStorageFormatterTestCase, self).setUp()
        self.endpoint = endpoint_storage.EndpointStorageFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.name = "app1"
        obj2.name = "app2"
        obj3.name = "app3"
        obj_list = [obj2, obj1, obj3]

        result = self.endpoint._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.name = mock.sentinel.name
        obj.additional_provider_properties = \
            mock.sentinel.additional_provider_properties

        result = self.endpoint._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.name,
                mock.sentinel.additional_provider_properties
            ),
            result
        )


class ListEndpointStorageTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Endpoint Storage."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListEndpointStorageTestCase, self).setUp()
        self.endpoint = endpoint_storage.ListEndpointStorage(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(cli_utils, 'add_args_for_json_option_to_parser')
    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_args_for_json_option_to_parser
    ):
        result = self.endpoint.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_args_for_json_option_to_parser.assert_called_once_with(
            mock_get_parser.return_value, 'environment')

    @mock.patch.object(endpoint_storage.EndpointStorageFormatter,
                       'list_objects')
    @mock.patch.object(cli_utils, 'get_option_value_from_args')
    def test_take_action(
        self,
        mock_get_option_value_from_args,
        mock_list_objects
    ):
        args = mock.Mock()
        args.options = mock.sentinel.options
        mock_endpoints = mock.Mock()
        mock_es = mock.Mock()
        self.mock_app.client_manager.coriolis.endpoints = mock_endpoints
        mock_es = self.mock_app.client_manager.coriolis.endpoint_storage

        result = self.endpoint.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_get_option_value_from_args.assert_called_once_with(
            args, 'environment', error_on_no_value=False)
        mock_es.list.assert_called_once_with(
            mock_endpoints.get_endpoint_id_for_name(args.endpoint),
            environment=mock_get_option_value_from_args.return_value
        )
        mock_list_objects.assert_called_once_with(mock_es.list.return_value)

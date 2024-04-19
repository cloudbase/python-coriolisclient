# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from cliff import command
from cliff import lister
from cliff import show
import ddt
from unittest import mock

from coriolisclient.cli import endpoints
from coriolisclient import exceptions
from coriolisclient.tests import test_base


@ddt.ddt
class EndpointTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Endpoints."""

    def test_add_connection_info_args_to_parser(self):
        mock_parser = mock.Mock()
        mock_add_argument = mock.Mock()
        mock_parser.add_mutually_exclusive_group.return_value.add_argument = \
            mock_add_argument

        result = endpoints.add_connection_info_args_to_parser(mock_parser)

        self.assertEqual(
            mock_parser,
            result
        )
        mock_parser.add_mutually_exclusive_group.assert_called_once()

    @ddt.data(
        {"conn": (None, None, None), "expected_result": None,
         "raise_if_none": False},
        {"conn": (None, None, None), "expected_result": "exception"},
        {
            "conn": ('{"conn_info": "mock_conn_info"}', None, None),
            "expected_result": {"conn_info": "mock_conn_info"}
        },
        {
            "conn": (None, '{"conn_info": "mock_conn_info"}', None),
            "expected_result": {"conn_info": "mock_conn_info"}
        },
        {
            "conn": (None, 'invalid', None),
            "expected_result": "exception"
        },
        {
            "conn": (None, None, "mock_secret"),
            "expected_result": {"secret_ref": "mock_secret"}
        },
    )
    def test_get_connnection_info_from_args(self, data):
        mock_args = mock.MagicMock()
        (mock_args.connection,
            mock_args.connection_file.__enter__.return_value.read.return_value,
            mock_args.connection_secret) = data["conn"]
        if data["conn"][1] is None:
            mock_args.connection_file = None

        if data["expected_result"] == "exception":
            self.assertRaises(
                ValueError,
                endpoints.get_connnection_info_from_args,
                mock_args
            )
        else:
            result = endpoints.get_connnection_info_from_args(
                mock_args, raise_if_none=data.get("raise_if_none", True))

            self.assertEqual(
                data["expected_result"],
                result
            )


class EndpointFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Endpoint Formatter."""

    def setUp(self):
        super(EndpointFormatterTestCase, self).setUp()
        self.endpoint = endpoints.EndpointFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.created_at = "date1"
        obj2.created_at = "date2"
        obj3.created_at = "date3"
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
        obj.type = mock.sentinel.type
        obj.description = mock.sentinel.description
        obj.mapped_regions = mock.sentinel.mapped_regions

        result = self.endpoint._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.name,
                mock.sentinel.type,
                mock.sentinel.description,
                mock.sentinel.mapped_regions
            ),
            result
        )


class EndpointDetailFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Endpoint Detail Formatter."""

    def setUp(self):
        super(EndpointDetailFormatterTestCase, self).setUp()
        self.endpoint = endpoints.EndpointDetailFormatter()

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.name = mock.sentinel.name
        obj.type = mock.sentinel.type
        obj.description = mock.sentinel.description
        obj.mapped_regions = mock.sentinel.mapped_regions
        obj.created_at = mock.sentinel.created_at
        obj.updated_at = mock.sentinel.updated_at
        obj.connection_info.to_dict = mock.Mock(
            return_value=mock.sentinel.connection_info
        )

        result = self.endpoint._get_formatted_data(obj)

        self.assertEqual(
            [
                mock.sentinel.id,
                mock.sentinel.name,
                mock.sentinel.type,
                mock.sentinel.description,
                mock.sentinel.connection_info,
                mock.sentinel.mapped_regions,
                mock.sentinel.created_at,
                mock.sentinel.updated_at
            ],
            result
        )


class CreateEndpointTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Create Endpoint."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CreateEndpointTestCase, self).setUp()
        self.endpoint = endpoints.CreateEndpoint(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(endpoints, 'add_connection_info_args_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_connection_info_args_to_parser
    ):
        result = self.endpoint.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_connection_info_args_to_parser.assert_called_once_with(
            mock_get_parser.return_value)

    @mock.patch.object(endpoints.EndpointDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(endpoints, 'get_connnection_info_from_args')
    def test_take_action(
        self,
        mock_get_connnection_info_from_args,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.connection_secret = mock.sentinel.connection_secret
        args.connection = None
        args.name = mock.sentinel.name
        args.provider = mock.sentinel.provider
        args.description = mock.sentinel.description
        args.regions = mock.sentinel.regions
        args.skip_validation = False
        mock_create = mock.Mock()
        mock_validate_connection = mock.Mock()
        mock_validate_connection.return_value = (True, "mock_message")
        self.mock_app.client_manager.coriolis.endpoints.create = mock_create
        self.mock_app.client_manager.coriolis.endpoints.validate_connection = \
            mock_validate_connection

        result = self.endpoint.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_get_connnection_info_from_args.assert_called_once_with(args)
        mock_create.assert_called_once_with(
            mock.sentinel.name,
            mock.sentinel.provider,
            mock_get_connnection_info_from_args.return_value,
            mock.sentinel.description,
            regions=mock.sentinel.regions,
        )
        mock_validate_connection.assert_called_once_with(
            mock_create.return_value.id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_create.return_value)

    def test_take_action_raises_connection(self):
        args = mock.Mock()
        args.connection_secret = mock.sentinel.connection_secret
        args.connection = mock.sentinel.connection

        self.assertRaises(
            exceptions.CoriolisException,
            self.endpoint.take_action,
            args
        )

    @mock.patch.object(endpoints.EndpointDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(endpoints, 'get_connnection_info_from_args')
    def test_take_action_validation_failed(
        self,
        mock_get_connnection_info_from_args,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.connection_secret = mock.sentinel.connection_secret
        args.connection = None
        args.name = mock.sentinel.name
        args.provider = mock.sentinel.provider
        args.description = mock.sentinel.description
        args.regions = mock.sentinel.regions
        args.skip_validation = False
        mock_create = mock.Mock()
        mock_validate_connection = mock.Mock()
        mock_validate_connection.return_value = (False, "mock_message")
        self.mock_app.client_manager.coriolis.endpoints.create = mock_create
        self.mock_app.client_manager.coriolis.endpoints.validate_connection = \
            mock_validate_connection

        self.assertRaises(
            exceptions.EndpointConnectionValidationFailed,
            self.endpoint.take_action,
            args
        )

        mock_get_connnection_info_from_args.assert_called_once_with(args)
        mock_create.assert_called_once_with(
            mock.sentinel.name,
            mock.sentinel.provider,
            mock_get_connnection_info_from_args.return_value,
            mock.sentinel.description,
            regions=mock.sentinel.regions,
        )
        mock_validate_connection.assert_called_once_with(
            mock_create.return_value.id)
        mock_get_formatted_entity.assert_not_called()


class UpdateEndpointTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Update Endpoint."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(UpdateEndpointTestCase, self).setUp()
        self.endpoint = endpoints.UpdateEndpoint(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(endpoints, 'add_connection_info_args_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_connection_info_args_to_parser
    ):
        result = self.endpoint.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_connection_info_args_to_parser.assert_called_once_with(
            mock_get_parser.return_value)

    @mock.patch.object(endpoints.EndpointDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(endpoints, 'get_connnection_info_from_args')
    def test_take_action(
        self,
        mock_get_connnection_info_from_args,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.connection_secret = mock.sentinel.connection_secret
        args.connection = None
        args.id = mock.sentinel.id
        args.name = mock.sentinel.name
        args.description = mock.sentinel.description
        args.regions = mock.sentinel.regions
        args.skip_validation = False
        mock_update = mock.Mock()
        self.mock_app.client_manager.coriolis.endpoints.update = mock_update
        expected_updated_values = {
            "name": mock.sentinel.name,
            "description": mock.sentinel.description,
            "connection_info": (mock_get_connnection_info_from_args.
                                return_value),
            "mapped_regions": mock.sentinel.regions,
        }

        result = self.endpoint.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_get_connnection_info_from_args.assert_called_once_with(
            args, raise_if_none=False)
        mock_update.assert_called_once_with(
            mock.sentinel.id,
            expected_updated_values,
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_update.return_value)

    def test_take_action_raises_connection(self):
        args = mock.Mock()
        args.connection_secret = mock.sentinel.connection_secret
        args.connection = mock.sentinel.connection

        self.assertRaises(
            exceptions.CoriolisException,
            self.endpoint.take_action,
            args
        )


class ShowEndpointTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Show Endpoint."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ShowEndpointTestCase, self).setUp()
        self.endpoint = endpoints.ShowEndpoint(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.endpoint.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(endpoints.EndpointDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        mock_client = mock.Mock()
        args.id = mock.sentinel.id
        self.mock_app.client_manager.coriolis.endpoints = mock_client

        result = self.endpoint.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_client.get_endpoint_id_for_name.assert_called_once_with(
            mock.sentinel.id)
        mock_client.get.assert_called_once_with(
            mock_client.get_endpoint_id_for_name.return_value)
        mock_get_formatted_entity.assert_called_once_with(
            mock_client.get.return_value)


class DeleteEndpointTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Delete Endpoint."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeleteEndpointTestCase, self).setUp()
        self.endpoint = endpoints.DeleteEndpoint(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.endpoint.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        mock_client = mock.Mock()
        args.id = mock.sentinel.id
        self.mock_app.client_manager.coriolis.endpoints = mock_client

        self.endpoint.take_action(args)

        mock_client.get_endpoint_id_for_name.assert_called_once_with(
            mock.sentinel.id)
        mock_client.delete.assert_called_once_with(
            mock_client.get_endpoint_id_for_name.return_value)


class ListEndpointTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Endpoint."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListEndpointTestCase, self).setUp()
        self.endpoint = endpoints.ListEndpoint(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.endpoint.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(endpoints.EndpointFormatter, 'list_objects')
    def test_take_action(self, mock_list_objects):
        args = mock.Mock()
        mock_client = mock.Mock()
        self.mock_app.client_manager.coriolis.endpoints = mock_client

        result = self.endpoint.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )

        mock_client.list.assert_called_once()
        mock_list_objects.assert_called_once_with(
            mock_client.list.return_value)


class EndpointValidateConnectionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Endpoint."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(EndpointValidateConnectionTestCase, self).setUp()
        self.endpoint = endpoints.EndpointValidateConnection(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.endpoint.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(endpoints.EndpointFormatter, 'list_objects')
    def test_take_action(self, mock_list_objects):
        args = mock.Mock()
        mock_endpoint = mock.Mock()
        args.id = mock.sentinel.id
        self.mock_app.client_manager.coriolis.endpoints = mock_endpoint
        mock_validate_connection = mock.Mock()
        mock_validate_connection.return_value = (True, "mock_message")
        self.mock_app.client_manager.coriolis.endpoints.validate_connection = \
            mock_validate_connection

        self.endpoint.take_action(args)

        mock_endpoint.get_endpoint_id_for_name.assert_called_once_with(
            mock.sentinel.id)
        mock_validate_connection.assert_called_once_with(
            mock_endpoint.get_endpoint_id_for_name.return_value)

    @mock.patch.object(endpoints.EndpointFormatter, 'list_objects')
    def test_take_action_not_valid(self, mock_list_objects):
        args = mock.Mock()
        mock_endpoint = mock.Mock()
        args.id = mock.sentinel.id
        self.mock_app.client_manager.coriolis.endpoints = mock_endpoint
        mock_validate_connection = mock.Mock()
        mock_validate_connection.return_value = (False, "mock_message")
        self.mock_app.client_manager.coriolis.endpoints.validate_connection = \
            mock_validate_connection

        self.assertRaisesRegex(
            exceptions.EndpointConnectionValidationFailed,
            "mock_message",
            self.endpoint.take_action,
            args
        )

        mock_endpoint.get_endpoint_id_for_name.assert_called_once_with(
            mock.sentinel.id)
        mock_validate_connection.assert_called_once_with(
            mock_endpoint.get_endpoint_id_for_name.return_value)

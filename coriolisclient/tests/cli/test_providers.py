# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from cliff import lister

from coriolisclient.cli import providers
from coriolisclient.tests import test_base


class ProvidersFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Providers Formatter."""

    def setUp(self):
        super(ProvidersFormatterTestCase, self).setUp()
        self.provider = providers.ProvidersFormatter()

    def test_get_sorted_list(self):
        obj1 = {"name": "name1"}
        obj2 = {"name": "name2"}
        obj3 = {"name": "name3"}
        obj_list = [obj2, obj1, obj3]

        result = self.provider._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = {
            "name": mock.sentinel.name,
            "types": [1, 2, -1]
        }

        with self.assertLogs(providers.LOG, level="DEBUG"):
            result = self.provider._get_formatted_data(obj)

            self.assertEqual(
                (
                    mock.sentinel.name,
                    "%s, %s" % (
                        providers.PROVIDERS_TYPE_FEATURE_MAP[1],
                        providers.PROVIDERS_TYPE_FEATURE_MAP[2])
                ),
                result
            )


class ProviderSchemasFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Providers Formatter."""

    def setUp(self):
        super(ProviderSchemasFormatterTestCase, self).setUp()
        self.provider = providers.ProviderSchemasFormatter()

    def test_get_formatted_data(self):
        obj = {
            "type": mock.sentinel.type,
            "schema": {
                "connection_info_schema": {"info": "mock_info"},
                "required": False
            }
        }

        result = self.provider._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.type,
                ('{\n'
                 '    "connection_info_schema": {\n'
                 '        "info": "mock_info"\n'
                 '    },\n'
                 '    "required": false\n}')
            ),
            result
        )


class ListProviderTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis List Provider."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListProviderTestCase, self).setUp()
        self.provider = providers.ListProvider(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
    ):
        result = self.provider.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(providers.ProvidersFormatter, 'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        mock_provider = mock.Mock()
        self.mock_app.client_manager.coriolis.providers = mock_provider

        result = self.provider.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_list_objects.assert_called_once_with(
            mock_provider.list.return_value.providers_list)


class ListProviderSchemasTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis List Provider Schemas."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListProviderSchemasTestCase, self).setUp()
        self.provider = providers.ListProviderSchemas(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
    ):
        result = self.provider.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(providers.ProviderSchemasFormatter, 'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        args.type = "connection"
        args.platform = mock.sentinel.platform
        mock_provider = mock.Mock()
        self.mock_app.client_manager.coriolis.providers = mock_provider

        result = self.provider.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_provider.schemas_list.assert_called_once_with(
            mock.sentinel.platform,
            providers.PROVIDER_SCHEMA_TYPE_MAP["connection"]
        )
        mock_obj = mock_provider.schemas_list.return_value.provider_schemas
        mock_list_objects(mock_obj.providers_list)

    def test_take_action_value_error(self):
        args = mock.Mock()
        args.type = "invalid"
        mock_provider = mock.Mock()
        self.mock_app.client_manager.coriolis.providers = mock_provider

        self.assertRaises(
            ValueError,
            self.provider.take_action,
            args
        )
        mock_provider.schemas_list.assert_not_called()

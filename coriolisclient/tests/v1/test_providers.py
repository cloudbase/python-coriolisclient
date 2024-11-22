# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import providers


class ProvidersTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Providers."""

    def test_properties(self):
        mock_client = mock.Mock()
        self.provider = providers.Providers(
            mock_client,
            {
                "provider1": {
                    "types": [mock.sentinel.type1, mock.sentinel.type2],
                },
                "provider2": {
                    "types": [mock.sentinel.type3, mock.sentinel.type4],
                }
            }
        )
        expected_provider_list = [
            {
                'name': 'provider1',
                'types': [mock.sentinel.type1, mock.sentinel.type2]
            },
            {
                'name': 'provider2',
                'types': [mock.sentinel.type3, mock.sentinel.type4]
            }
        ]
        expected_provider_schemas = [
            {
                'schema': {
                    'types': [mock.sentinel.type1, mock.sentinel.type2]},
                'type': 'provider1'
            },
            {
                'schema': {
                    'types': [mock.sentinel.type3, mock.sentinel.type4]},
                'type': 'provider2'
            }
        ]

        self.assertEqual(
            (expected_provider_list, expected_provider_schemas),
            (self.provider.providers_list, self.provider.provider_schemas)
        )


class ProvidersManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Providers Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(ProvidersManagerTestCase, self).setUp()
        self.provider = providers.ProvidersManager(mock_client)

    @mock.patch.object(providers.ProvidersManager, "_get")
    def test_list(self, mock_get):
        result = self.provider.list()

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with("/providers", "providers")

    @mock.patch.object(providers.ProvidersManager, "_get")
    def test_schemas_list(self, mock_get):
        result = self.provider.schemas_list(
            mock.sentinel.provider_name, mock.sentinel.provider_type)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            '/providers/%s/schemas/%s' % (mock.sentinel.provider_name,
                                          mock.sentinel.provider_type),
            "schemas")

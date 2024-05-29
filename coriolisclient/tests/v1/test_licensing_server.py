# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import licensing
from coriolisclient.v1 import licensing_server


class LicensingServerManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Licensing Server Manager."""

    @mock.patch.object(licensing, 'LicensingClient')
    def setUp(self, mock_LicensingClient):
        mock_client = mock.Mock()
        self.mock_licencing_client = mock.Mock()
        mock_LicensingClient.return_value = self.mock_licencing_client
        super(LicensingServerManagerTestCase, self).setUp()
        self.licence = licensing_server.LicensingServerManager(
            mock_client)

    def test_status(self):
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.status()

        self.assertEqual(
            mock_resource_class.return_value,
            result
        )
        self.mock_licencing_client.get.assert_called_once_with(
            '/status',
            response_key='status')
        mock_resource_class.assert_called_once_with(
            self.licence, self.mock_licencing_client.get.return_value,
            loaded=True)

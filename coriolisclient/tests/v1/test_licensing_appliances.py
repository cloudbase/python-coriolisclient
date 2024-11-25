# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import licensing
from coriolisclient.v1 import licensing_appliances


class LicensingAppliancesManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Licensing Appliances Manager."""

    @mock.patch.object(licensing, 'LicensingClient')
    def setUp(self, mock_LicensingClient):
        mock_client = mock.Mock()
        self.mock_licencing_client = mock.Mock()
        mock_LicensingClient.return_value = self.mock_licencing_client
        super(LicensingAppliancesManagerTestCase, self).setUp()
        self.licence = licensing_appliances.LicensingAppliancesManager(
            mock_client)

    def test_list(self):
        self.licence._licensing_cli.get.return_value = {
            "appliance1": "mock_appliance1",
            "appliance2": "mock_appliance2"
        }
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.list()

        self.assertEqual(
            [mock_resource_class.return_value,
             mock_resource_class.return_value],
            result
        )
        self.mock_licencing_client.get.assert_called_once_with(
            '/appliances', response_key='appliances')
        mock_resource_class.assert_has_calls([
            mock.call(self.licence, "appliance1", loaded=True),
            mock.call(self.licence, "appliance2", loaded=True)
        ])

    def test_show(self):
        self.licence._licensing_cli.get.return_value = mock.sentinel.data
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.show(mock.sentinel.appliance_id)

        self.assertEqual(
            mock_resource_class.return_value,
            result
        )
        self.mock_licencing_client.get.assert_called_once_with(
            '/appliances/%s' % mock.sentinel.appliance_id,
            response_key='appliance')
        mock_resource_class.assert_called_once_with(
            self.licence, mock.sentinel.data, loaded=True
        )

    def test_create(self):
        self.licence._licensing_cli.post.return_value = mock.sentinel.data
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.create()

        self.assertEqual(
            mock_resource_class.return_value,
            result
        )
        self.mock_licencing_client.post.assert_called_once_with(
            '/appliances', response_key='appliance')
        mock_resource_class.assert_called_once_with(
            self.licence, mock.sentinel.data, loaded=True
        )

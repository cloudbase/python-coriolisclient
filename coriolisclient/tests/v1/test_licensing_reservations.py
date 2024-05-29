# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import licensing
from coriolisclient.v1 import licensing_reservations


class LicensingReservationsManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Licensing Reservations Manager."""

    @mock.patch.object(licensing, 'LicensingClient')
    def setUp(self, mock_LicensingClient):
        mock_client = mock.Mock()
        self.mock_licencing_client = mock.Mock()
        mock_LicensingClient.return_value = self.mock_licencing_client
        super(LicensingReservationsManagerTestCase, self).setUp()
        self.licence = licensing_reservations.LicensingReservationsManager(
            mock_client)

    def test_list(self):
        self.licence._licensing_cli.get.return_value = {
            "reservation1": "mock_reservation1",
            "reservation2": "mock_reservation2"
        }
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.list(mock.sentinel.appliance_id)

        self.assertEqual(
            [mock_resource_class.return_value,
             mock_resource_class.return_value],
            result
        )
        self.mock_licencing_client.get.assert_called_once_with(
            '/appliances/%s/reservations' % mock.sentinel.appliance_id,
            response_key='reservations')
        mock_resource_class.assert_has_calls([
            mock.call(self.licence, "reservation1", loaded=True),
            mock.call(self.licence, "reservation2", loaded=True)
        ])

    def test_show(self):
        self.licence._licensing_cli.get.return_value = mock.sentinel.data
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.show(
            mock.sentinel.appliance_id, mock.sentinel.reservation_id)

        self.assertEqual(
            mock_resource_class.return_value,
            result
        )
        self.mock_licencing_client.get.assert_called_once_with(
            '/appliances/%s/reservations/%s' % (mock.sentinel.appliance_id,
                                                mock.sentinel.reservation_id),
            response_key='reservation')
        mock_resource_class.assert_called_once_with(
            self.licence, mock.sentinel.data, loaded=True
        )

    def test_refresh(self):
        self.licence._licensing_cli.post.return_value = mock.sentinel.data
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.refresh(
            mock.sentinel.appliance_id, mock.sentinel.reservation_id)

        self.assertEqual(
            mock_resource_class.return_value,
            result
        )
        self.mock_licencing_client.post.assert_called_once_with(
            '/appliances/%s/reservations/%s/refresh' %
            (mock.sentinel.appliance_id, mock.sentinel.reservation_id),
            response_key='reservation')
        mock_resource_class.assert_called_once_with(
            self.licence, mock.sentinel.data, loaded=True
        )

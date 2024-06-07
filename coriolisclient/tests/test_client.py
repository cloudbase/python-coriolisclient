# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient import client as coriolis_client
from coriolisclient.tests import test_base


class _HTTPClientTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis HTTP Client."""

    def test__init__(self):
        session = mock.Mock()
        self.client = coriolis_client._HTTPClient(
            session, endpoint=mock.sentinel.endpoint, version='v0')
        self.assertEqual(
            "%s/%s" % (mock.sentinel.endpoint, 'v0'),
            self.client.endpoint_override
        )

    def test__init__no_endpoint(self):
        session = mock.Mock()
        self.client = coriolis_client._HTTPClient(session)
        self.assertEqual(
            None,
            self.client.endpoint_override
        )


class ClientTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client."""

    @mock.patch.object(coriolis_client, "_HTTPClient")
    def test__init__(self, mock_HTTPClient):
        try:
            self.client = coriolis_client.Client(session=mock.sentinel.session)
        except Exception:
            self.fail("Failed to initialize Client")
        mock_HTTPClient.assert_called_once_with(session=mock.sentinel.session)

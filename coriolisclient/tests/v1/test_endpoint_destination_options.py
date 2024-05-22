# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import endpoint_destination_options


class EndpointDestinationOptionsManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Endpoint Destination Options Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(EndpointDestinationOptionsManagerTestCase, self).setUp()
        self.endpoint = (
            endpoint_destination_options.
            EndpointDestinationOptionsManager)(mock_client)

    @mock.patch.object(endpoint_destination_options.
                       EndpointDestinationOptionsManager, '_list')
    def test_list(
        self,
        mock_list
    ):
        mock_endpoint = mock.Mock()
        mock_endpoint.uuid = '53773ab8-1474-4cf7-bf0c-a496a6595ecb'

        result = self.endpoint.list(
            mock_endpoint,
            environment={"env": "mock_env"},
            option_names=["option1", "option2"]
        )

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            ('/endpoints/53773ab8-1474-4cf7-bf0c-a496a6595ecb/'
             'destination-options'
             '?env=eyJlbnYiOiAibW9ja19lbnYifQ=='
             '&options=WyJvcHRpb24xIiwgIm9wdGlvbjIiXQ=='),
            'destination_options')

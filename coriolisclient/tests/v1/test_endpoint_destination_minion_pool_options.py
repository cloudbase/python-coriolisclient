# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import endpoint_destination_minion_pool_options


class EndpointDestinationMinionPoolOptionsManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """
    Test suite for the Coriolis v1 Endpoint Destination Minion Pool Options
    Manager.
    """

    def setUp(self):
        mock_client = mock.Mock()
        super(EndpointDestinationMinionPoolOptionsManagerTestCase, self
              ).setUp()
        self.endpoint = (
            endpoint_destination_minion_pool_options.
            EndpointDestinationMinionPoolOptionsManager)(mock_client)

    @mock.patch.object(endpoint_destination_minion_pool_options.
                       EndpointDestinationMinionPoolOptionsManager, '_list')
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
             'destination-minion-pool-options'
             '?env=eyJlbnYiOiAibW9ja19lbnYifQ=='
             '&options=WyJvcHRpb24xIiwgIm9wdGlvbjIiXQ=='),
            'destination_minion_pool_options')

# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import endpoint_source_minion_pool_options


class EndpointSourceMinionPoolOptionsManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """
    Test suite for the Coriolis v1 Endpoint Source Minion Pool Options
    Manager.
    """

    def setUp(self):
        mock_client = mock.Mock()
        super(EndpointSourceMinionPoolOptionsManagerTestCase, self
              ).setUp()
        self.endpoint = (
            endpoint_source_minion_pool_options.
            EndpointSourceMinionPoolOptionsManager)(mock_client)

    @mock.patch.object(endpoint_source_minion_pool_options.
                       EndpointSourceMinionPoolOptionsManager, '_list')
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
             'source-minion-pool-options'
             '?env=eyJlbnYiOiAibW9ja19lbnYifQ=='
             '&options=WyJvcHRpb24xIiwgIm9wdGlvbjIiXQ=='),
            'source_minion_pool_options')

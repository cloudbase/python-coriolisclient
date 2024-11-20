# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient import base
from coriolisclient.tests import test_base
from coriolisclient.v1 import common
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
    @mock.patch.object(common, 'encode_base64_param')
    @mock.patch.object(base, 'getid')
    def test_list(
        self,
        mock_getid,
        mock_encode_base64_param,
        mock_list
    ):
        mock_endpoint = mock.Mock()
        mock_getid.return_value = mock.sentinel.id
        mock_encode_base64_param.side_effect = [
            mock.sentinel.encoded_env, mock.sentinel.encoded_option_names]

        result = self.endpoint.list(
            mock_endpoint,
            mock.sentinel.environment,
            mock.sentinel.option_names
        )

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            ('/endpoints/sentinel.id/destination-minion-pool-options'
             '?env=sentinel.encoded_env'
             '&options=sentinel.encoded_option_names'),
            'destination_minion_pool_options')

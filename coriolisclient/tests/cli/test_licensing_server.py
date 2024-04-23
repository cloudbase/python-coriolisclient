# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from cliff import show

from coriolisclient.cli import licensing_server
from coriolisclient.tests import test_base


class ServerStatusFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Server Formatter."""

    def setUp(self):
        super(ServerStatusFormatterTestCase, self).setUp()
        self.server = licensing_server.ServerStatusFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.hostname = "host1"
        obj2.hostname = "host2"
        obj3.hostname = "host3"
        obj_list = [obj2, obj1, obj3]

        result = self.server._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.hostname = mock.sentinel.hostname
        obj.multi_appliance = mock.sentinel.multi_appliance
        obj.supported_licence_versions = \
            mock.sentinel.supported_licence_versions
        obj.server_local_time = mock.sentinel.server_local_time

        result = self.server._get_formatted_data(obj)

        self.assertEqual(
            [
                mock.sentinel.hostname,
                mock.sentinel.multi_appliance,
                mock.sentinel.supported_licence_versions,
                mock.sentinel.server_local_time,
            ],
            result
        )


class ServerStatusTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Server Status."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ServerStatusTestCase, self).setUp()
        self.server = licensing_server.ServerStatus(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.server.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing_server.ServerStatusFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        mock_licensing_server = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing_server = \
            mock_licensing_server

        result = self.server.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_licensing_server.status.return_value)

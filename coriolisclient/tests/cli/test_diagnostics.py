# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from cliff import lister
from unittest import mock

from coriolisclient.cli import diagnostics
from coriolisclient.tests import test_base


class DiagnosticsFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Diagnostics."""

    def setUp(self):
        super(DiagnosticsFormatterTestCase, self).setUp()
        self.diag = diagnostics.DiagnosticsFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.application = "app1"
        obj2.application = "app2"
        obj3.application = "app3"
        obj_list = [obj2, obj1, obj3]

        result = self.diag._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.application = mock.sentinel.application
        obj.hostname = mock.sentinel.hostname
        obj.ip_addresses = mock.sentinel.ip_addresses
        obj.packages = mock.sentinel.packages
        obj.os_info = mock.sentinel.os_info

        result = self.diag._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.application,
                mock.sentinel.hostname,
                mock.sentinel.ip_addresses,
                mock.sentinel.packages,
                mock.sentinel.os_info
            ),
            result
        )


class GetCoriolisDiagnosticsTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Get Coriolis Diagnostics."""

    @mock.patch.object(lister.Lister, '__init__')
    def setUp(self, mock__init__):
        mock__init__.return_value = None
        super(GetCoriolisDiagnosticsTestCase, self).setUp()
        self.diag = diagnostics.GetCoriolisDiagnostics()

    @mock.patch.object(diagnostics.GetCoriolisDiagnostics, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.diag.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(diagnostics.DiagnosticsFormatter, 'list_objects')
    def test_take_action(self, mock_list_objects):
        mock_app = mock.Mock()
        self.diag.app = mock_app
        result = self.diag.take_action(mock.sentinel.prog_name)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        (mock_app.client_manager.coriolis.diagnostics.get.
         assert_called_once)()
        mock_list_objects.assert_called_once_with(
            mock_app.client_manager.coriolis.diagnostics.get.return_value)

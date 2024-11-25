# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import diagnostics


class DiagnosticsManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Diagnostics Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(DiagnosticsManagerTestCase, self).setUp()
        self.diag = diagnostics.DiagnosticsManager(mock_client)

    @mock.patch.object(diagnostics.DiagnosticsManager, '_list')
    def test_get(self, mock_list):
        result = self.diag.get()

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with('/diagnostics', 'diagnostics')

# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolisclient.cli import diagnostics
from coriolisclient.tests import test_base


class DiagnosticsFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Diagnostics."""

    def setUp(self):
        super(DiagnosticsFormatterTestCase, self).setUp()
        self.diagnostics = diagnostics.DiagnosticsFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj1.application = "app1"
        obj2.application = "app2"
        obj_list = [obj2, obj1]

        result = self.diagnostics._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2],
            result
        )

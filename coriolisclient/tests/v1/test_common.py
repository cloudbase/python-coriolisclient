# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import ddt

from coriolisclient import exceptions
from coriolisclient.tests import test_base
from coriolisclient.v1 import common


class TaskTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Task."""

    def setUp(self):
        super(TaskTestCase, self).setUp()
        self.task = common.Task(
            None,
            {
                "progress_updates": [
                    {"progress_update1": "mock_update1"},
                    {"progress_update2": "mock_update2"}
                ]
            },
            loaded=False
        )

    def test_progress_updates(self):
        result = self.task.progress_updates

        self.assertEqual(
            ("mock_update1", "mock_update2"),
            (result[0].progress_update1, result[1].progress_update2)
        )


@ddt.ddt
class CommonTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Common."""

    @ddt.data(
        ("value", False, "dmFsdWU="),
        ({"key": "value"}, True, "eyJrZXkiOiAidmFsdWUifQ==")
    )
    @ddt.unpack
    def test_encode_base64_param(self, param, is_json, expected_result):
        result = common.encode_base64_param(param, is_json=is_json)

        self.assertEqual(
            result,
            expected_result
        )

    @ddt.data(
        (12345, False),
        (None, False),
        ({"key value"}, True)
    )
    @ddt.unpack
    def test_encode_base64_param_raises(self, param, is_json):
        self.assertRaises(
            exceptions.CoriolisException,
            common.encode_base64_param,
            param,
            is_json=is_json
        )

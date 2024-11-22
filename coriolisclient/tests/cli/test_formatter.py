# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import ddt
from unittest import mock

from coriolisclient.cli import formatter
from coriolisclient.tests import test_base


class TestEntityFormattter(formatter.EntityFormatter):

    def __init__(self):
        self.columns = [
            "column_1",
            "column_2"
        ]

    def _get_formatted_data(self, obj):
        return obj


@ddt.ddt
class TestEntityFormattterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Entity Formatter."""

    def setUp(self):
        super(TestEntityFormattterTestCase, self).setUp()
        self.format = TestEntityFormattter()

    def test_get_sorted_list(self):
        obj_list = ["obj2", "obj1"]

        result = self.format._get_sorted_list(obj_list)

        self.assertEqual(
            obj_list,
            result
        )

    def test_list_objects(self):
        obj_list = ["obj2", "obj1"]

        (columns, data) = self.format.list_objects(obj_list)

        self.assertEqual(
            (
                self.format.columns,
                ["obj2", "obj1"]
            ),
            (
                columns,
                list(data)
            )
        )

    def test_get_generic_data(self):
        obj = mock.Mock()

        result = self.format._get_generic_data(obj)

        self.assertEqual(
            obj,
            result
        )

    def test_get_generic_columns(self):
        result = self.format._get_generic_columns()

        self.assertEqual(
            self.format.columns,
            result
        )

    def test_get_formatted_entity(self):
        obj = mock.Mock()

        (columns, data) = self.format.get_formatted_entity(obj)

        self.assertEqual(
            (self.format.columns, obj),
            (columns, data)
        )

    @ddt.data(
        {
            "current_value": 3,
            "max_value": 9,
            "percent_format": "{:.0f}%",
            "expected_result": "33%"
        },
        {
            "current_value": 3,
            "max_value": 9,
            "percent_format": "{:.2f}%",
            "expected_result": "33.33%"
        },
        {
            "current_value": 0,
            "max_value": 9,
            "percent_format": "{:.0f}%",
            "expected_result": None
        },
        {
            "current_value": 3,
            "max_value": None,
            "percent_format": "{:.0f}%",
            "expected_result": None
        }
    )
    def test_get_percent_string(self, data):
        result = self.format._get_percent_string(
            data["current_value"],
            data["max_value"],
            percent_format=data["percent_format"]
        )

        self.assertEqual(
            data["expected_result"],
            result
        )

    @mock.patch.object(formatter.EntityFormatter, '_get_percent_string')
    def test_format_progress_update(self, mock_get_percent_string):
        progress_update = {
            "current_step": "mock_current_step",
            "total_steps": "mock_total_steps",
            "created_at": "mock_created_at",
            "message": "mock_message",
        }
        mock_get_percent_string.return_value = "mock_percent_string"

        result = self.format._format_progress_update(progress_update)

        self.assertEqual(
            "mock_created_at [mock_percent_string] mock_message",
            result
        )

    @mock.patch.object(formatter.EntityFormatter, '_get_percent_string')
    def test_format_progress_update_no_percent_string(
        self,
        mock_get_percent_string
    ):
        progress_update = {
            "current_step": "mock_current_step",
            "total_steps": "mock_total_steps",
            "created_at": "mock_created_at",
            "message": "mock_message",
        }
        mock_get_percent_string.return_value = None

        result = self.format._format_progress_update(progress_update)

        self.assertEqual(
            "mock_created_at mock_message",
            result
        )

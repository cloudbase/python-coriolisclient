# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import argparse
import ddt
import os
from unittest import mock

from coriolisclient.cli import utils
from coriolisclient.tests import test_base


@ddt.ddt
class UtilsTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Utils."""

    def test_add_storage_mappings_arguments_to_parser(self):
        parser = argparse.ArgumentParser()

        utils.add_storage_mappings_arguments_to_parser(parser)
        args = parser.parse_args(
            ['--storage-backend-mapping', 'mock_source=mock_destination',
             '--disk-storage-mapping', 'mock_disk_id=mock_destination',
             '--default-storage-backend', 'mock_default_storage_backend'])

        self.assertEqual(
            [{'disk_id': 'mock_disk_id', 'destination': 'mock_destination'}],
            args.disk_storage_mappings
        )
        self.assertEqual(
            [{'source': 'mock_source', 'destination': 'mock_destination'}],
            args.storage_backend_mappings
        )
        self.assertEqual(
            'mock_default_storage_backend',
            args.default_storage_backend
        )

    def test_get_storage_mappings_dict_from_args(self):
        args = mock.Mock()
        args.default_storage_backend = mock.sentinel.default_storage_backend
        args.disk_storage_mappings = mock.sentinel.disk_storage_mappings
        args.storage_backend_mappings = mock.sentinel.storage_backend_mappings

        result = utils.get_storage_mappings_dict_from_args(args)

        self.assertEqual(
            {
                "backend_mappings": mock.sentinel.storage_backend_mappings,
                "default": mock.sentinel.default_storage_backend,
                "disk_mappings": mock.sentinel.disk_storage_mappings
            },
            result
        )

    def test_format_mapping(self):
        mapping = {
            "mapping1": "mock_mapping1",
            "mapping2": "mock_mapping2",
            "mapping3": "mock_mapping3"
        }

        result = utils.format_mapping(mapping)

        self.assertEqual(
            (
                "'mapping1'='mock_mapping1', "
                "'mapping2'='mock_mapping2', "
                "'mapping3'='mock_mapping3'"
            ),
            result
        )

    def test_parse_storage_mappings(self):
        storage_mappings = {
            "default": "mock_default",
            "backend_mappings": [
                {
                    "source": "mock_source",
                    "destination": "mock_destination"
                }
            ],
            "disk_mappings": [
                {
                    "disk_id": "mock_disk_id",
                    "destination": "mock_destination"
                }
            ]
        }

        result = utils.parse_storage_mappings(storage_mappings)

        self.assertEqual(
            (
                'mock_default',
                {'mock_source': 'mock_destination'},
                {'mock_disk_id': 'mock_destination'}
            ),
            result
        )

    def test_parse_storage_mappings_none(self):
        result = utils.parse_storage_mappings(None)

        self.assertEqual(
            (None, {}, {}),
            result
        )

    def test_format_json_for_object_property(self):
        obj = mock.Mock()
        obj.prop_name = {"key1": "value1", "key2": "value2"}

        result = utils.format_json_for_object_property(obj, "prop_name")

        self.assertEqual(
            '{\n  "key1": "value1",\n  "key2": "value2"\n}',
            result
        )

    def test_format_json_for_object_property_to_dict(self):
        obj = mock.Mock()
        obj.prop_name.to_dict.return_value = \
            {"key1": "value1", "key2": "value2"}

        result = utils.format_json_for_object_property(obj, "prop_name")

        self.assertEqual(
            '{\n  "key1": "value1",\n  "key2": "value2"\n}',
            result
        )

    def test_format_json_for_object_property_none(self):
        obj = mock.Mock()
        obj.prop_name = None

        result = utils.format_json_for_object_property(obj, "prop_name")

        self.assertEqual(
            '{}',
            result
        )

    def test_validate_uuid_string(self):
        result = utils.validate_uuid_string(
            "12345678-9ABC-DEF1-2345-6789abcdef12")

        self.assertEqual(
            True,
            result
        )

        result = utils.validate_uuid_string(
            "123456789ABCDEF")

        self.assertEqual(
            False,
            result
        )

    @mock.patch.object(argparse, 'FileType')
    def test_add_args_for_json_option_to_parser(self, mock_file_type):
        parser = argparse.ArgumentParser()

        utils.add_args_for_json_option_to_parser(
            parser, "option_name")

        args = parser.parse_args(
            ['--option-name', 'mock_option'])

        args_file = parser.parse_args(
            ['--option-name-file', 'mock_option_file'])

        self.assertEqual(
            ('mock_option', mock_file_type.return_value.return_value),
            (args.option_name, args_file.option_name_file)
        )

    def test_get_option_value_from_args(self):
        args = mock.MagicMock()
        args.option_name = '{"option": "raw_value"}'
        args.option_name_file.__enter__.return_value.read.return_value = \
            '{"option": "file_value"}'

        result = utils.get_option_value_from_args(args, "option-name")

        self.assertEqual(
            {'option': 'raw_value'},
            result
        )

        args.option_name = None

        result = utils.get_option_value_from_args(args, "option-name")

        self.assertEqual(
            {'option': 'file_value'},
            result
        )

    def test_get_option_value_from_args_no_value(self):
        args = mock.Mock()
        args.option_name = None
        args.option_name_file = None

        result = utils.get_option_value_from_args(
            args, "option-name", error_on_no_value=False)

        self.assertEqual(
            None,
            result
        )

        self.assertRaises(
            ValueError,
            utils.get_option_value_from_args,
            args,
            "option-name"
        )

    def test_get_option_value_from_args_json_value_error(self):
        args = mock.Mock()
        args.option_name = "invalid"
        args.option_name_file = None

        self.assertRaises(
            ValueError,
            utils.get_option_value_from_args,
            args,
            "option-name"
        )

    @ddt.data(
        {
            "global_scripts": None,
            "instance_scripts": None,
            "expected_result":
            {
                "global": {},
                "instances": {}
            }
        },
        {
            "global_scripts": ["linux="],
            "instance_scripts": ["instance_1="],
            "expected_result":
            {
                "global": {"linux": None},
                "instances": {"instance_1": None}
            }
        },
        {
            "global_scripts": ["linux script"],
            "instance_scripts": ["linux script"],
            "expected_result":
            {
                "global": {},
                "instances": {}
            }
        },
        {
            "global_scripts": ["invalid_os=scrips"],
            "instance_scripts": None,
            "expected_result": None
        },
        {
            "global_scripts": ["linux='invalid/file/path'"],
            "instance_scripts": None,
            "expected_result": None
        },
        {
            "global_scripts": None,
            "instance_scripts": ["linux='invalid/file/path'"],
            "expected_result": None
        },
    )
    def test_compose_user_scripts(self, data):
        global_scripts = data["global_scripts"]
        instance_scripts = data["instance_scripts"]
        expected_result = data["expected_result"]

        if expected_result:
            result = utils.compose_user_scripts(
                global_scripts, instance_scripts)

            self.assertEqual(
                expected_result,
                result
            )
        else:
            self.assertRaises(
                ValueError,
                utils.compose_user_scripts,
                global_scripts,
                instance_scripts
            )

    def test_compose_user_scripts_from_file(self):
        script_path = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.join(script_path, 'data/user_scripts.yml')
        global_scripts = ["linux=%s" % script_path]
        instance_scripts = ["linux=%s" % script_path]

        result = utils.compose_user_scripts(global_scripts, instance_scripts)

        self.assertEqual(
            {
                'global': {'linux': '"mock_script1"\n"mock_script2"\n'},
                'instances': {'linux': '"mock_script1"\n"mock_script2"\n'}
            },
            result
        )

    def test_add_minion_pool_args_to_parser(self):
        parser = argparse.ArgumentParser()

        utils.add_minion_pool_args_to_parser(parser)
        args = parser.parse_args(
            ['--osmorphing-minion-pool-mapping',
             'mock_instance_id=mock_pool_id'])

        self.assertEqual(
            [{'instance_id': 'mock_instance_id', 'pool_id': 'mock_pool_id'}],
            args.instance_osmorphing_minion_pool_mappings
        )

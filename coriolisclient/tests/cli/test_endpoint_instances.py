# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from cliff import lister
from cliff import show
from unittest import mock

from coriolisclient.cli import endpoint_instances
from coriolisclient.cli import utils as cli_utils
from coriolisclient.tests import test_base


class EndpointInstanceFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Endpoint Instance Formatter."""

    def setUp(self):
        super(EndpointInstanceFormatterTestCase, self).setUp()
        self.endpoint = endpoint_instances.EndpointInstanceFormatter()

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.flavor_name = mock.sentinel.flavor_name
        obj.memory_mb = mock.sentinel.memory_mb
        obj.num_cpu = mock.sentinel.num_cpu
        obj.os_type = mock.sentinel.os_type
        obj.to_dict = mock.Mock(
            return_value={"instance_name": mock.sentinel.instance_name}
        )

        result = self.endpoint._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.instance_name,
                mock.sentinel.flavor_name,
                mock.sentinel.memory_mb,
                mock.sentinel.num_cpu,
                mock.sentinel.os_type
            ),
            result
        )


class InstancesDetailFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Instances Detail Formatter."""

    def setUp(self):
        super(InstancesDetailFormatterTestCase, self).setUp()
        self.endpoint = endpoint_instances.InstancesDetailFormatter()

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.name = mock.sentinel.name
        obj.flavor_name = mock.sentinel.flavor_name
        obj.memory_mb = mock.sentinel.memory_mb
        obj.num_cpu = mock.sentinel.num_cpu
        obj.os_type = mock.sentinel.os_type
        obj.to_dict = mock.Mock(
            return_value={"instance_name": mock.sentinel.instance_name,
                          "firmware_type": mock.sentinel.firmware_type}
        )
        devices = {
            "controllers": ["controller1", "controller2"],
            "disks": ["disk1", "disk2"],
            "nics": ["nic1", "nic2"],
            "cdroms": ["cdrom1", "cdrom2"],
            "floppies": ["floppy1", "floppy2"],
            "serial_ports": ["serial_port1", "serial_port2"]
        }
        obj.devices = devices

        result = self.endpoint._get_formatted_data(obj)

        self.assertEqual(
            [
                mock.sentinel.id,
                mock.sentinel.name,
                mock.sentinel.instance_name,
                mock.sentinel.flavor_name,
                mock.sentinel.memory_mb,
                mock.sentinel.num_cpu,
                mock.sentinel.os_type,
                mock.sentinel.firmware_type,
                '[\n  "controller1",\n  "controller2"\n]',
                '[\n  "disk1",\n  "disk2"\n]',
                '[\n  "nic1",\n  "nic2"\n]',
                '[\n  "cdrom1",\n  "cdrom2"\n]',
                '[\n  "floppy1",\n  "floppy2"\n]',
                '[\n  "serial_port1",\n  "serial_port2"\n]'
            ],
            result
        )


class ListEndpointInstanceTestCase(
        test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Endpoint Instance."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListEndpointInstanceTestCase, self).setUp()
        self.endpoint = endpoint_instances.ListEndpointInstance(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(cli_utils, 'add_args_for_json_option_to_parser')
    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_args_for_json_option_to_parser
    ):
        result = self.endpoint.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_args_for_json_option_to_parser.assert_called_once_with(
            mock_get_parser.return_value, 'environment')

    @mock.patch.object(endpoint_instances.EndpointInstanceFormatter,
                       'list_objects')
    @mock.patch.object(cli_utils, 'get_option_value_from_args')
    def test_take_action(
        self,
        mock_get_option_value_from_args,
        mock_list_objects
    ):
        args = mock.Mock()
        args.marker = mock.sentinel.marker
        args.limit = mock.sentinel.limit
        args.name = mock.sentinel.name
        mock_endpoints = mock.Mock()
        mock_ei = mock.Mock()
        self.mock_app.client_manager.coriolis.endpoints = mock_endpoints
        mock_ei = self.mock_app.client_manager.coriolis.endpoint_instances

        result = self.endpoint.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_get_option_value_from_args.assert_called_once_with(
            args, 'environment', error_on_no_value=False)
        mock_ei.list.assert_called_once_with(
            mock_endpoints.get_endpoint_id_for_name(args.endpoint),
            mock_get_option_value_from_args.return_value,
            mock.sentinel.marker,
            mock.sentinel.limit,
            mock.sentinel.name
        )
        mock_list_objects.assert_called_once_with(mock_ei.list.return_value)


class ShowEndpointInstanceTestCase(
        test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Show Endpoint Instance"""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ShowEndpointInstanceTestCase, self).setUp()
        self.endpoint = endpoint_instances.ShowEndpointInstance(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(cli_utils, 'add_args_for_json_option_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_args_for_json_option_to_parser
    ):
        result = self.endpoint.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_args_for_json_option_to_parser.assert_called_once_with(
            mock_get_parser.return_value, 'environment')

    @mock.patch.object(endpoint_instances.InstancesDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(cli_utils, 'get_option_value_from_args')
    def test_take_action(
        self,
        mock_get_option_value_from_args,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.instance = mock.sentinel.instance
        mock_endpoints = mock.Mock()
        mock_ei = mock.Mock()
        self.mock_app.client_manager.coriolis.endpoints = mock_endpoints
        mock_ei = self.mock_app.client_manager.coriolis.endpoint_instances

        result = self.endpoint.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_get_option_value_from_args.assert_called_once_with(
            args, 'environment', error_on_no_value=False)
        mock_ei.get.assert_called_once_with(
            mock_endpoints.get_endpoint_id_for_name(args.endpoint),
            mock.sentinel.instance,
            mock_get_option_value_from_args.return_value,
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_ei.get.return_value)

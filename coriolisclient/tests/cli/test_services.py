# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import services
from coriolisclient.tests import test_base


class ServicesTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Services."""

    def test_add_service_enablement_args_to_parser(self):
            parser = mock.Mock()

            services._add_service_enablement_args_to_parser(parser)

            parser.add_mutually_exclusive_group.assert_called_once()


class ServiceFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Services Formatter."""

    def setUp(self):
        super(ServiceFormatterTestCase, self).setUp()
        self.service = services.ServiceFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.created_at = "date1"
        obj2.created_at = "date2"
        obj3.created_at = "date3"
        obj_list = [obj2, obj1, obj3]

        result = self.service._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.host = mock.sentinel.host
        obj.binary = mock.sentinel.binary
        obj.topic = mock.sentinel.topic
        obj.enabled = mock.sentinel.enabled
        obj.status = mock.sentinel.status
        obj.mapped_regions = mock.sentinel.mapped_regions
        obj.created_at = mock.sentinel.created_at
        obj.updated_at = mock.sentinel.updated_at

        result = self.service._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.host,
                mock.sentinel.binary,
                mock.sentinel.topic,
                mock.sentinel.enabled,
                mock.sentinel.status,
                mock.sentinel.mapped_regions,
                mock.sentinel.created_at,
                mock.sentinel.updated_at
            ),
            result
        )


class CreateServiceTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Create Service."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CreateServiceTestCase, self).setUp()
        self.service = services.CreateService(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(services, '_add_service_enablement_args_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_service_enablement_args_to_parser
    ):
        result = self.service.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_service_enablement_args_to_parser.assert_called_once_with(
            mock_get_parser.return_value)

    @mock.patch.object(services.ServiceFormatter, 'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.host = mock.sentinel.host
        args.binary = mock.sentinel.binary
        args.topic = mock.sentinel.topic
        args.enabled = True
        args.regions = mock.sentinel.regions
        mock_services = mock.Mock()
        self.mock_app.client_manager.coriolis.services = mock_services

        result = self.service.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_services.create.assert_called_once_with(
            mock.sentinel.host,
            mock.sentinel.binary,
            topic=mock.sentinel.topic,
            enabled=True,
            regions=mock.sentinel.regions
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_services.create.return_value)


class UpdateServiceTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Update Service."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(UpdateServiceTestCase, self).setUp()
        self.service = services.UpdateService(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(services, '_add_service_enablement_args_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_service_enablement_args_to_parser
    ):
        result = self.service.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_service_enablement_args_to_parser.assert_called_once_with(
            mock_get_parser.return_value)

    @mock.patch.object(services.ServiceFormatter, 'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.id = mock.sentinel.id
        args.enabled = True
        args.regions = mock.sentinel.regions
        mock_services = mock.Mock()
        self.mock_app.client_manager.coriolis.services = mock_services
        expected_updated_values = {
            "enabled": True,
            "mapped_regions": mock.sentinel.regions,
        }

        result = self.service.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_services.update.assert_called_once_with(
            mock.sentinel.id,
            expected_updated_values
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_services.update.return_value)


class ShowServiceTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Show Service."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ShowServiceTestCase, self).setUp()
        self.service = services.ShowService(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.service.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(services.ServiceFormatter, 'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_services = mock.Mock()
        self.mock_app.client_manager.coriolis.services = mock_services

        result = self.service.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_services.get.assert_called_once_with(mock.sentinel.id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_services.get.return_value)


class DeleteServiceTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Delete Service."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeleteServiceTestCase, self).setUp()
        self.service = services.DeleteService(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.service.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_services = mock.Mock()
        self.mock_app.client_manager.coriolis.services = mock_services

        self.service.take_action(args)

        mock_services.delete.assert_called_once_with(mock.sentinel.id)


class ListServicesTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis List Services."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListServicesTestCase, self).setUp()
        self.service = services.ListServices(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.service.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(services.ServiceFormatter, 'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        mock_services = mock.Mock()
        self.mock_app.client_manager.coriolis.services = mock_services

        result = self.service.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_list_objects.assert_called_once_with(
            mock_services.list.return_value)

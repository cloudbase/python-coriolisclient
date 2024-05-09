# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import regions
from coriolisclient.tests import test_base


class RegionsTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Regions."""

    def test_add_region_enablement_args_to_parser(self):
            parser = mock.Mock()

            regions._add_region_enablement_args_to_parser(parser)

            parser.add_mutually_exclusive_group.assert_called_once()


class RegionFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Regions Formatter."""

    def setUp(self):
        super(RegionFormatterTestCase, self).setUp()
        self.region = regions.RegionFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.created_at = "date1"
        obj2.created_at = "date2"
        obj3.created_at = "date3"
        obj_list = [obj2, obj1, obj3]

        result = self.region._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.name = mock.sentinel.name
        obj.enabled = mock.sentinel.enabled
        obj.description = mock.sentinel.description
        obj.mapped_endpoints = mock.sentinel.mapped_endpoints
        obj.mapped_services = mock.sentinel.mapped_services
        obj.created_at = mock.sentinel.created_at
        obj.updated_at = mock.sentinel.updated_at

        result = self.region._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.name,
                mock.sentinel.enabled,
                mock.sentinel.description,
                mock.sentinel.mapped_endpoints,
                mock.sentinel.mapped_services,
                mock.sentinel.created_at,
                mock.sentinel.updated_at
            ),
            result
        )


class CreateRegionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Create Region."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CreateRegionTestCase, self).setUp()
        self.region = regions.CreateRegion(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(regions, '_add_region_enablement_args_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_region_enablement_args_to_parser
    ):
        result = self.region.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_region_enablement_args_to_parser.assert_called_once_with(
            mock_get_parser.return_value)

    @mock.patch.object(regions.RegionFormatter, 'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.name = mock.sentinel.name
        args.description = mock.sentinel.description
        args.enabled = True
        mock_regions = mock.Mock()
        self.mock_app.client_manager.coriolis.regions = mock_regions

        result = self.region.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_regions.create.assert_called_once_with(
            mock.sentinel.name,
            description=mock.sentinel.description,
            enabled=True
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_regions.create.return_value)


class UpdateRegionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Update Region."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(UpdateRegionTestCase, self).setUp()
        self.region = regions.UpdateRegion(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(regions, '_add_region_enablement_args_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_region_enablement_args_to_parser
    ):
        result = self.region.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_region_enablement_args_to_parser.assert_called_once_with(
            mock_get_parser.return_value)

    @mock.patch.object(regions.RegionFormatter, 'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.id = mock.sentinel.id
        args.enabled = True
        args.name = mock.sentinel.name
        args.description = mock.sentinel.description
        mock_regions = mock.Mock()
        self.mock_app.client_manager.coriolis.regions = mock_regions
        expected_updated_values = {
            "enabled": True,
            "name": mock.sentinel.name,
            "description": mock.sentinel.description,
        }

        result = self.region.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_regions.update.assert_called_once_with(
            mock.sentinel.id,
            expected_updated_values
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_regions.update.return_value)


class ShowRegionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Show Region."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ShowRegionTestCase, self).setUp()
        self.region = regions.ShowRegion(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.region.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(regions.RegionFormatter, 'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_regions = mock.Mock()
        self.mock_app.client_manager.coriolis.regions = mock_regions

        result = self.region.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_regions.get.assert_called_once_with(mock.sentinel.id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_regions.get.return_value)


class DeleteRegionTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Delete Region."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeleteRegionTestCase, self).setUp()
        self.region = regions.DeleteRegion(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.region.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_regions = mock.Mock()
        self.mock_app.client_manager.coriolis.regions = mock_regions

        self.region.take_action(args)

        mock_regions.delete.assert_called_once_with(mock.sentinel.id)


class ListRegionsTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis List Regions."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListRegionsTestCase, self).setUp()
        self.region = regions.ListRegions(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.region.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(regions.RegionFormatter, 'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        mock_regions = mock.Mock()
        self.mock_app.client_manager.coriolis.regions = mock_regions

        result = self.region.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_list_objects.assert_called_once_with(
            mock_regions.list.return_value)

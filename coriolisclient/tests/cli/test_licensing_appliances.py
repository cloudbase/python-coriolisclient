# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from cliff import lister
from cliff import show

from coriolisclient.cli import licensing_appliances
from coriolisclient.tests import test_base


class ApplianceFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Appliance Formatter."""

    def setUp(self):
        super(ApplianceFormatterTestCase, self).setUp()
        self.appliance = licensing_appliances.ApplianceFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.id = "app1"
        obj2.id = "app2"
        obj3.id = "app3"
        obj_list = [obj2, obj1, obj3]

        result = self.appliance._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id

        result = self.appliance._get_formatted_data(obj)

        self.assertEqual(
            [mock.sentinel.id],
            result
        )


class ApplianceListTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Appliance List."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ApplianceListTestCase, self).setUp()
        self.appliance = licensing_appliances.ApplianceList(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.appliance.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing_appliances.ApplianceFormatter,
                       'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        mock_licensing_appliances = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing_appliances = \
            mock_licensing_appliances

        result = self.appliance.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_list_objects.assert_called_once_with(
            mock_licensing_appliances.list.return_value)


class ApplianceShowTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Appliance Show."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ApplianceShowTestCase, self).setUp()
        self.appliance = licensing_appliances.ApplianceShow(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.appliance.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing_appliances.ApplianceFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.appliance_id = mock.sentinel.appliance_id
        mock_licensing_appliances = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing_appliances = \
            mock_licensing_appliances

        result = self.appliance.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_licensing_appliances.show.assert_called_once_with(
            mock.sentinel.appliance_id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_licensing_appliances.show.return_value)


class ApplianceCreateTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Appliance Create."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ApplianceCreateTestCase, self).setUp()
        self.appliance = licensing_appliances.ApplianceCreate(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.appliance.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing_appliances.ApplianceFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        mock_licensing_appliances = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing_appliances = \
            mock_licensing_appliances

        result = self.appliance.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_licensing_appliances.create.return_value)

# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import licensing
from coriolisclient.tests import test_base


class LicensingStatusFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Licensing Status Formatter."""

    def setUp(self):
        super(LicensingStatusFormatterTestCase, self).setUp()
        self.licence = licensing.LicensingStatusFormatter()

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.appliance_id = mock.sentinel.appliance_id
        obj.earliest_licence_expiry_time = \
            mock.sentinel.earliest_licence_expiry_time
        obj.latest_licence_expiry_time = \
            mock.sentinel.latest_licence_expiry_time
        obj.current_performed_migrations = \
            mock.sentinel.current_performed_migrations
        obj.current_performed_replicas = \
            mock.sentinel.current_performed_replicas
        obj.current_available_migrations = \
            mock.sentinel.current_available_migrations
        obj.current_available_replicas = \
            mock.sentinel.current_available_replicas
        obj.lifetime_performed_migrations = \
            mock.sentinel.lifetime_performed_migrations
        obj.lifetime_performed_replicas = \
            mock.sentinel.lifetime_performed_replicas
        obj.lifetime_available_migrations = \
            mock.sentinel.lifetime_available_migrations
        obj.lifetime_available_replicas = \
            mock.sentinel.lifetime_available_replicas

        result = self.licence._get_formatted_data(obj)

        self.assertEqual(
            [
                mock.sentinel.appliance_id,
                mock.sentinel.earliest_licence_expiry_time,
                mock.sentinel.latest_licence_expiry_time,
                mock.sentinel.current_performed_migrations,
                mock.sentinel.current_performed_replicas,
                mock.sentinel.current_available_migrations,
                mock.sentinel.current_available_replicas,
                mock.sentinel.lifetime_performed_migrations,
                mock.sentinel.lifetime_performed_replicas,
                mock.sentinel.lifetime_available_migrations,
                mock.sentinel.lifetime_available_replicas
            ],
            result
        )


class LicenceFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Licence Formatter."""

    def setUp(self):
        super(LicenceFormatterTestCase, self).setUp()
        self.licence = licensing.LicenceFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.period_end = "period_end1"
        obj2.period_end = "period_end2"
        obj3.period_end = "period_end3"
        obj_list = [obj2, obj1, obj3]

        result = self.licence._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.issue_date = mock.sentinel.issue_date
        obj.migrations = mock.sentinel.migrations
        obj.replicas = mock.sentinel.replicas
        obj.period_start = mock.sentinel.period_start
        obj.period_end = mock.sentinel.period_end
        obj.period_duration = mock.sentinel.period_duration
        obj.licence_version = mock.sentinel.licence_version

        result = self.licence._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.issue_date,
                mock.sentinel.migrations,
                mock.sentinel.replicas,
                mock.sentinel.period_start,
                mock.sentinel.period_end,
                mock.sentinel.period_duration,
                mock.sentinel.licence_version
            ),
            result
        )


class LicensingApplianceStatusTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Licensing Appliance Status."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(LicensingApplianceStatusTestCase, self).setUp()
        self.licence = licensing.LicensingApplianceStatus(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.licence.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing.LicensingStatusFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.appliance_id = mock.sentinel.appliance_id
        mock_lic_status = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing.status = \
            mock_lic_status

        result = self.licence.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_lic_status.assert_called_once_with(mock.sentinel.appliance_id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_lic_status.return_value)


class LicenceRegisterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Licence Register."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(LicenceRegisterTestCase, self).setUp()
        self.licence = licensing.LicenceRegister(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.licence.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing.LicenceFormatter, 'get_formatted_entity')
    def test_take_action_raw_arg(
        self,
        mock_get_formatted_entity
    ):
        args = mock.MagicMock()
        args.licence_pem = mock.sentinel.licence_pem
        args.licence_pem_file.__enter__.return_value.read.return_value = \
            mock.sentinel.licence_pem_file
        mock_licence = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing.register = mock_licence

        result = self.licence.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_licence.assert_called_once_with(
            args.appliance_id, mock.sentinel.licence_pem)
        mock_get_formatted_entity.assert_called_once_with(
            mock_licence.return_value)

    @mock.patch.object(licensing.LicenceFormatter, 'get_formatted_entity')
    def test_take_action_file_arg(
        self,
        mock_get_formatted_entity
    ):
        args = mock.MagicMock()
        args.licence_pem = None
        args.licence_pem_file.__enter__.return_value.read.return_value = \
            mock.sentinel.licence_pem_file
        mock_licence = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing.register = mock_licence

        result = self.licence.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_licence.assert_called_once_with(
            args.appliance_id, mock.sentinel.licence_pem_file)
        mock_get_formatted_entity.assert_called_once_with(
            mock_licence.return_value)

    def test_take_action_value_error(self):
        args = mock.MagicMock()
        args.licence_pem = None
        args.licence_pem_file = None
        mock_licence = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing.register = mock_licence

        self.assertRaises(
            ValueError,
            self.licence.take_action,
            args
        )

        mock_licence.assert_not_called()


class LicenceListTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Licence List."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(LicenceListTestCase, self).setUp()
        self.licence = licensing.LicenceList(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.licence.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing.LicenceFormatter, 'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        args.appliance_id = mock.sentinel.appliance_id
        mock_lic_list = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing.list = \
            mock_lic_list

        result = self.licence.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_lic_list.assert_called_once_with(mock.sentinel.appliance_id)
        mock_list_objects.assert_called_once_with(mock_lic_list.return_value)


class LicenceShowTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Licence Show."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(LicenceShowTestCase, self).setUp()
        self.licence = licensing.LicenceShow(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.licence.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing.LicenceFormatter, 'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.appliance_id = mock.sentinel.appliance_id
        args.licence_id = mock.sentinel.licence_id
        licence = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing.show = licence

        result = self.licence.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        licence.assert_called_once_with(args.appliance_id, args.licence_id)
        mock_get_formatted_entity.assert_called_once_with(licence.return_value)


class LicenceDeleteTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Licence Delete."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(LicenceDeleteTestCase, self).setUp()
        self.licence = licensing.LicenceDelete(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.licence.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.appliance_id = mock.sentinel.appliance_id
        args.licence_id = mock.sentinel.licence_id
        licence = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing.delete = licence

        self.licence.take_action(args)

        licence.assert_called_once_with(args.appliance_id, args.licence_id)

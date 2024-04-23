# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from cliff import lister
from cliff import show

from coriolisclient.cli import licensing_reservations
from coriolisclient.tests import test_base


class ReservationFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Reservation Formatter."""

    def setUp(self):
        super(ReservationFormatterTestCase, self).setUp()
        self.reservation = licensing_reservations.ReservationFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.created_at = "date1"
        obj2.created_at = "date2"
        obj3.created_at = "date3"
        obj_list = [obj2, obj1, obj3]

        result = self.reservation._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.appliance_id = mock.sentinel.appliance_id
        obj.licence_id = mock.sentinel.licence_id
        obj.type = mock.sentinel.type
        obj.count = mock.sentinel.count
        obj.created_at = mock.sentinel.created_at

        result = self.reservation._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.appliance_id,
                mock.sentinel.licence_id,
                mock.sentinel.type,
                mock.sentinel.count,
                mock.sentinel.created_at
            ),
            result
        )


class ReservationListTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Reservation List."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ReservationListTestCase, self).setUp()
        self.reservation = licensing_reservations.ReservationList(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.reservation.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing_reservations.ReservationFormatter,
                       'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        mock_licensing_reservations = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing_reservations = \
            mock_licensing_reservations

        result = self.reservation.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_list_objects.assert_called_once_with(
            mock_licensing_reservations.list.return_value)


class ReservationShowTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Reservation Show."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ReservationShowTestCase, self).setUp()
        self.reservation = licensing_reservations.ReservationShow(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.reservation.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing_reservations.ReservationFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.appliance_id = mock.sentinel.appliance_id
        args.reservation_id = mock.sentinel.reservation_id
        mock_licensing_reservations = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing_reservations = \
            mock_licensing_reservations

        result = self.reservation.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_licensing_reservations.show.assert_called_once_with(
            args.appliance_id, args.reservation_id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_licensing_reservations.show.return_value)


class ReservationRefreshTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Reservation Refresh."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ReservationRefreshTestCase, self).setUp()
        self.reservation = licensing_reservations.ReservationRefresh(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser
    ):
        result = self.reservation.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(licensing_reservations.ReservationFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        mock_licensing_reservations = mock.Mock()
        self.mock_app.client_manager.coriolis.licensing_reservations = \
            mock_licensing_reservations

        result = self.reservation.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_licensing_reservations.refresh.return_value)

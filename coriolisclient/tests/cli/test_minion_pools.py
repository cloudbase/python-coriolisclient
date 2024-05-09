# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import os
from unittest import mock

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import minion_pools
from coriolisclient.cli import utils as cli_utils
from coriolisclient.tests import test_base


class MinionPoolFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Minion Pool Formatter."""

    def setUp(self):
        super(MinionPoolFormatterTestCase, self).setUp()
        self.minion = minion_pools.MinionPoolFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.created_at = "date1"
        obj2.created_at = "date2"
        obj3.created_at = "date3"
        obj_list = [obj2, obj1, obj3]

        result = self.minion._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.name = mock.sentinel.name
        obj.endpoint_id = mock.sentinel.endpoint_id
        obj.platform = mock.sentinel.platform
        obj.os_type = mock.sentinel.os_type
        obj.notes = mock.sentinel.notes
        obj.status = mock.sentinel.status
        obj.minimum_minions = 1
        obj.maximum_minions = 2

        result = self.minion._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.name,
                mock.sentinel.endpoint_id,
                mock.sentinel.platform,
                mock.sentinel.os_type,
                mock.sentinel.notes,
                mock.sentinel.status,
                "1 - 2",
            ),
            result
        )


class MinionPoolDetailFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Minion Pool Detail Formatter."""

    def setUp(self):
        super(MinionPoolDetailFormatterTestCase, self).setUp()
        self.minion = minion_pools.MinionPoolDetailFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.created_at = "date1"
        obj2.created_at = "date2"
        obj3.created_at = "date3"
        obj_list = [obj2, obj1, obj3]

        result = self.minion._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_format_pool_event(self):
        event = {
            "level": "mock_level",
            "created_at": "mock_date",
            "message": "mock_message",
        }
        expected_result = "mock_level mock_date mock_message"

        result = self.minion._format_pool_event(event)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(minion_pools.MinionPoolDetailFormatter,
                       '_format_pool_event')
    def test_format_pool_events(self, mock_format_pool_event):
        event1 = {
            "level": "mock_level1",
            "created_at": "mock_date1",
            "message": "mock_message1",
            "index": 1
        }
        event2 = {
            "level": "mock_level2",
            "created_at": "mock_date2",
            "message": "mock_message2",
            "index": 2
        }
        event3 = {
            "level": "mock_level3",
            "created_at": "mock_date3",
            "message": "mock_message3",
            "index": 3
        }
        ret_event1 = "mock_level1 mock_date1 mock_message1"
        ret_event2 = "mock_level2 mock_date2 mock_message2"
        ret_event3 = "mock_level3 mock_date3 mock_message3"
        events = [event3, event1, event2]
        mock_format_pool_event.side_effect = [
            ret_event1, ret_event2, ret_event3]
        expected_result = (
            "mock_level1 mock_date1 mock_message1%(ls)s"
            "mock_level2 mock_date2 mock_message2%(ls)s"
            "mock_level3 mock_date3 mock_message3" % {"ls": os.linesep})

        result = self.minion._format_pool_events(events)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(minion_pools.MinionPoolDetailFormatter,
                       '_format_progress_update')
    def test__format_progress_updates(self, mock_format_progress_update):
        update1 = {"created_at": "date2", "message2": "message2"}
        update2 = {"created_at": "date3", "message3": "message3"}
        update3 = {"index": 2, "created_at": "date1"}
        ret_update1 = "date2 [10] message2"
        ret_update2 = "date3 [20] message3"
        ret_update3 = "date1 [30] None"
        progress_updates = [update3, update1, update2]
        mock_format_progress_update.side_effect = [
            ret_update1, ret_update2, ret_update3]
        expected_result = (
            'date2 [10] message2%(ls)sdate3 [20] message3%(ls)s'
            'date1 [30] None' % {"ls": os.linesep}
        )

        result = self.minion._format_progress_updates(progress_updates)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(minion_pools.MinionPoolDetailFormatter,
                       '_format_pool_events')
    @mock.patch.object(minion_pools.MinionPoolDetailFormatter,
                       '_format_progress_updates')
    @mock.patch.object(cli_utils, 'format_json_for_object_property')
    def test_get_formatted_data(
        self,
        mock_format_json_for_object_property,
        mock_format_progress_updates,
        mock_format_pool_events
    ):
        mock_obj = mock.Mock()
        mock_obj.id = mock.sentinel.id
        mock_obj.name = mock.sentinel.name
        mock_obj.endpoint_id = mock.sentinel.endpoint_id
        mock_obj.platform = mock.sentinel.platform
        mock_obj.os_type = mock.sentinel.os_type
        mock_obj.status = mock.sentinel.status
        mock_obj.notes = mock.sentinel.notes
        mock_obj.created_at = mock.sentinel.created_at
        mock_obj.updated_at = mock.sentinel.updated_at
        mock_obj.maintenance_trust_id = mock.sentinel.maintenance_trust_id
        mock_obj.minimum_minions = mock.sentinel.minimum_minions
        mock_obj.maximum_minions = mock.sentinel.maximum_minions
        mock_obj.minion_max_idle_time = mock.sentinel.minion_max_idle_time
        mock_obj.minion_retention_strategy = \
            mock.sentinel.minion_retention_strategy
        mock_format_json_for_object_property.side_effect = [
            mock.sentinel.environment_options,
            mock.sentinel.shared_resources,
            mock.sentinel.minion_machines,
        ]
        mock_format_pool_events.return_value = \
            mock.sentinel.formatted_pool_events
        mock_format_progress_updates.return_value = \
            mock.sentinel.formatted_progress_updates
        mock_obj.info = mock.sentinel.info
        expected_result = (
            mock.sentinel.id,
            mock.sentinel.name,
            mock.sentinel.endpoint_id,
            mock.sentinel.platform,
            mock.sentinel.os_type,
            mock.sentinel.status,
            mock.sentinel.notes,
            mock.sentinel.created_at,
            mock.sentinel.updated_at,
            mock.sentinel.maintenance_trust_id,
            mock.sentinel.minimum_minions,
            mock.sentinel.maximum_minions,
            mock.sentinel.minion_max_idle_time,
            mock.sentinel.minion_retention_strategy,
            mock.sentinel.environment_options,
            mock.sentinel.shared_resources,
            mock.sentinel.formatted_pool_events,
            mock.sentinel.formatted_progress_updates,
            mock.sentinel.minion_machines,
        )

        result = self.minion._get_formatted_data(mock_obj)

        self.assertEqual(
            expected_result,
            result
        )


class CreateMinionPoolTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Create Minion Pool."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CreateMinionPoolTestCase, self).setUp()
        self.minion = minion_pools.CreateMinionPool(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(cli_utils, 'add_args_for_json_option_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_args_for_json_option_to_parser
    ):
        result = self.minion.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_args_for_json_option_to_parser.assert_called_once_with(
            mock_get_parser.return_value, "environment-options")

    @mock.patch.object(minion_pools.MinionPoolDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(cli_utils, 'get_option_value_from_args')
    def test_take_action(
        self,
        mock_get_option_value_from_args,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.name = mock.sentinel.name
        args.platform = mock.sentinel.platform
        args.os_type = mock.sentinel.os_type
        args.minimum_minions = mock.sentinel.minimum_minions
        args.maximum_minions = mock.sentinel.maximum_minions
        args.minion_max_idle_time = mock.sentinel.minion_max_idle_time
        args.minion_retention_strategy = \
            mock.sentinel.minion_retention_strategy
        args.notes = mock.sentinel.notes
        args.skip_allocation = mock.sentinel.skip_allocation
        args.endpoint_id = mock.sentinel.endpoint_id
        mock_endpoints = mock.Mock()
        mock_endpoints.get_endpoint_id_for_name.return_value = \
            mock.sentinel.endpoint_id
        self.mock_app.client_manager.coriolis.endpoints = mock_endpoints
        mock_minion_pool = mock.Mock()
        self.mock_app.client_manager.coriolis.minion_pools = \
            mock_minion_pool

        result = self.minion.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_get_option_value_from_args.assert_called_once_with(
            args, 'environment-options', error_on_no_value=True)
        mock_endpoints.get_endpoint_id_for_name.assert_called_once_with(
            mock.sentinel.endpoint_id)
        mock_minion_pool.create.assert_called_once_with(
            mock.sentinel.name,
            mock.sentinel.endpoint_id,
            mock.sentinel.platform,
            mock.sentinel.os_type,
            mock_get_option_value_from_args.return_value,
            minimum_minions=mock.sentinel.minimum_minions,
            maximum_minions=mock.sentinel.maximum_minions,
            minion_max_idle_time=mock.sentinel.minion_max_idle_time,
            minion_retention_strategy=mock.sentinel.minion_retention_strategy,
            notes=mock.sentinel.notes,
            skip_allocation=mock.sentinel.skip_allocation
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_minion_pool.create.return_value)


class UpdateMinionPoolTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Update Minion Pool."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(UpdateMinionPoolTestCase, self).setUp()
        self.minion = minion_pools.UpdateMinionPool(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(cli_utils, 'add_args_for_json_option_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        mock_add_args_for_json_option_to_parser
    ):
        result = self.minion.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)
        mock_add_args_for_json_option_to_parser.assert_called_once_with(
            mock_get_parser.return_value, "environment-options")

    @mock.patch.object(minion_pools.MinionPoolDetailFormatter,
                       'get_formatted_entity')
    @mock.patch.object(cli_utils, 'get_option_value_from_args')
    def test_take_action(
        self,
        mock_get_option_value_from_args,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.id = mock.sentinel.id
        args.name = mock.sentinel.name
        args.os_type = mock.sentinel.os_type
        args.minimum_minions = mock.sentinel.minimum_minions
        args.maximum_minions = mock.sentinel.maximum_minions
        args.minion_max_idle_time = mock.sentinel.minion_max_idle_time
        args.minion_retention_strategy = \
            mock.sentinel.minion_retention_strategy
        args.notes = mock.sentinel.notes
        args.environment_options = mock.sentinel.environment_options
        mock_minion_pool = mock.Mock()
        self.mock_app.client_manager.coriolis.minion_pools = \
            mock_minion_pool
        mock_get_option_value_from_args.return_value = \
            mock.sentinel.environment_options
        expected_updated_values = {
            "name": mock.sentinel.name,
            "os_type": mock.sentinel.os_type,
            "minimum_minions": mock.sentinel.minimum_minions,
            "maximum_minions": mock.sentinel.maximum_minions,
            "minion_max_idle_time": mock.sentinel.minion_max_idle_time,
            "minion_retention_strategy":
            mock.sentinel.minion_retention_strategy,
            "notes": mock.sentinel.notes,
            "environment_options": mock.sentinel.environment_options
        }

        result = self.minion.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_get_option_value_from_args.assert_called_once_with(
            args, 'environment-options', error_on_no_value=False)
        mock_minion_pool.update.assert_called_once_with(
            mock.sentinel.id,
            expected_updated_values
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_minion_pool.update.return_value)


class ShowMinionPoolTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Show Minion Pool."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ShowMinionPoolTestCase, self).setUp()
        self.minion = minion_pools.ShowMinionPool(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
    ):
        result = self.minion.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(minion_pools.MinionPoolDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_minion_pool = mock.Mock()
        self.mock_app.client_manager.coriolis.minion_pools = \
            mock_minion_pool

        result = self.minion.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_minion_pool.get.assert_called_once_with(mock.sentinel.id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_minion_pool.get.return_value)


class DeleteMinionPoolTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Delete Minion Pool."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeleteMinionPoolTestCase, self).setUp()
        self.minion = minion_pools.DeleteMinionPool(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
    ):
        result = self.minion.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_minion_pool = mock.Mock()
        self.mock_app.client_manager.coriolis.minion_pools = \
            mock_minion_pool

        self.minion.take_action(args)

        mock_minion_pool.delete.assert_called_once_with(mock.sentinel.id)


class ListMinionPoolsTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis List Minion Pools."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListMinionPoolsTestCase, self).setUp()
        self.minion = minion_pools.ListMinionPools(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
    ):
        result = self.minion.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(minion_pools.MinionPoolFormatter,
                       'list_objects')
    def test_take_action(
        self,
        mock_list_objects
    ):
        args = mock.Mock()
        mock_minion_pool = mock.Mock()
        self.mock_app.client_manager.coriolis.minion_pools = \
            mock_minion_pool

        result = self.minion.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_list_objects.assert_called_once_with(
            mock_minion_pool.list.return_value)


class AllocateMinionPoolTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Allocate Minion Pool."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(AllocateMinionPoolTestCase, self).setUp()
        self.minion = minion_pools.AllocateMinionPool(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
    ):
        result = self.minion.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(minion_pools.MinionPoolDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_minion_pool = mock.Mock()
        self.mock_app.client_manager.coriolis.minion_pools = \
            mock_minion_pool

        result = self.minion.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_minion_pool.allocate_minion_pool.assert_called_once_with(
            mock.sentinel.id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_minion_pool.allocate_minion_pool.return_value)


class RefreshMinionPoolTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Refresh Minion Pool."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(RefreshMinionPoolTestCase, self).setUp()
        self.minion = minion_pools.RefreshMinionPool(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
    ):
        result = self.minion.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(minion_pools.MinionPoolDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_minion_pool = mock.Mock()
        self.mock_app.client_manager.coriolis.minion_pools = \
            mock_minion_pool

        result = self.minion.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_minion_pool.refresh_minion_pool.assert_called_once_with(
            mock.sentinel.id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_minion_pool.refresh_minion_pool.return_value)


class DeallocateMinionPoolTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Deallocate Minion Pool."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeallocateMinionPoolTestCase, self).setUp()
        self.minion = minion_pools.DeallocateMinionPool(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
    ):
        result = self.minion.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(minion_pools.MinionPoolDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity
    ):
        args = mock.Mock()
        args.id = mock.sentinel.id
        args.force = mock.sentinel.force
        mock_minion_pool = mock.Mock()
        self.mock_app.client_manager.coriolis.minion_pools = \
            mock_minion_pool

        result = self.minion.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_minion_pool.deallocate_minion_pool.assert_called_once_with(
            mock.sentinel.id, force=mock.sentinel.force)
        mock_get_formatted_entity.assert_called_once_with(
            mock_minion_pool.deallocate_minion_pool.return_value)

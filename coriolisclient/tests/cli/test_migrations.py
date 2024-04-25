# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import os
from unittest import mock

from cliff import command
from cliff import lister
from cliff import show

from coriolisclient.cli import formatter
from coriolisclient.cli import migrations
from coriolisclient.cli import utils as cli_utils
from coriolisclient.tests import test_base


class MigrationFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Migration Formatter."""

    def setUp(self):
        super(MigrationFormatterTestCase, self).setUp()
        self.migration = migrations.MigrationFormatter()

    def test_get_sorted_list(self):
        obj1 = mock.Mock()
        obj2 = mock.Mock()
        obj3 = mock.Mock()
        obj1.created_at = "date1"
        obj2.created_at = "date2"
        obj3.created_at = "date3"
        obj_list = [obj2, obj1, obj3]

        result = self.migration._get_sorted_list(obj_list)

        self.assertEqual(
            [obj1, obj2, obj3],
            result
        )

    def test_get_formatted_data(self):
        obj = mock.Mock()
        obj.id = mock.sentinel.id
        obj.last_execution_status = mock.sentinel.last_execution_status
        obj.instances = ["mock_instance3", "mock_instance1", "mock_instance2"]
        obj.notes = mock.sentinel.notes
        obj.created_at = mock.sentinel.created_at

        result = self.migration._get_formatted_data(obj)

        self.assertEqual(
            (
                mock.sentinel.id,
                mock.sentinel.last_execution_status,
                ('mock_instance3%(ls)smock_instance1%(ls)smock_instance2'
                 % {"ls": os.linesep}),
                mock.sentinel.notes,
                mock.sentinel.created_at
            ),
            result
        )


class MigrationDetailFormatterTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Migration Detail Formatter."""

    def setUp(self):
        super(MigrationDetailFormatterTestCase, self).setUp()
        self.migration = migrations.MigrationDetailFormatter(
            show_instances_data=True)

    def test_format_instances(self):
        obj = mock.Mock()
        obj.instances = ["mock_instance3", "mock_instance1", "mock_instance2"]
        expected_result = (
            'mock_instance1%(ls)smock_instance2%(ls)smock_instance3'
            % {"ls": os.linesep}
        )

        result = self.migration._format_instances(obj)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(formatter.EntityFormatter, '_format_progress_update')
    def test_format_progress_updates(self, mock_format_progress_update):
        update1 = {"created_at": "date2", "message2": "message2"}
        update2 = {"created_at": "date3", "message3": "message3"}
        update3 = {"index": 2, "created_at": "date1"}
        ret_update1 = "date2 [10] message2"
        ret_update2 = "date3 [20] message3"
        ret_update3 = "date1 [30] None"
        task_dict = {"progress_updates": [update3, update1, update2]}
        mock_format_progress_update.side_effect = [
            ret_update1, ret_update2, ret_update3]
        expected_result = (
            'date2 [10] message2%(ls)sdate3 [20] message3%(ls)s'
            'date1 [30] None' % {"ls": os.linesep}
        )

        result = self.migration._format_progress_updates(task_dict)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(migrations.MigrationDetailFormatter,
                       '_format_progress_updates')
    def test_format_task(self, mock_format_progress_updates):
        mock_task = mock.Mock()
        task = {
            "depends_on": ["mock_dep1", "mock_dep2"],
            "id": mock.sentinel.id,
            "task_type": mock.sentinel.task_type,
            "instance": mock.sentinel.instance,
            "status": mock.sentinel.status,
            "exception_details": mock.sentinel.exception_details
        }
        mock_task.to_dict.return_value = task
        mock_format_progress_updates.return_value = (
            'date2 [10] message2%(ls)sdate3 [20] message3%(ls)s'
            'date1 [30] None' % {"ls": os.linesep}
        )
        expected_result = (
            'id: sentinel.id%(ls)s'
            'task_type: sentinel.task_type%(ls)s'
            'instance: sentinel.instance%(ls)s'
            'status: sentinel.status%(ls)s'
            'depends_on: mock_dep1, mock_dep2%(ls)s'
            'exception_details: sentinel.exception_details%(ls)s'
            'progress_updates:%(ls)s'
            'date2 [10] message2%(ls)s'
            'date3 [20] message3%(ls)s'
            'date1 [30] None' % {"ls": os.linesep})

        result = self.migration._format_task(mock_task)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(migrations.MigrationDetailFormatter,
                       '_format_progress_updates')
    def test_format_task_no_progress_updates(
        self, mock_format_progress_updates):
        mock_task = mock.Mock()
        task = {
            "depends_on": ["mock_dep1", "mock_dep2"],
            "id": mock.sentinel.id,
            "task_type": mock.sentinel.task_type,
            "instance": mock.sentinel.instance,
            "status": mock.sentinel.status,
            "exception_details": mock.sentinel.exception_details
        }
        mock_task.to_dict.return_value = task
        mock_format_progress_updates.return_value = None
        expected_result = (
            'id: sentinel.id%(ls)s'
            'task_type: sentinel.task_type%(ls)s'
            'instance: sentinel.instance%(ls)s'
            'status: sentinel.status%(ls)s'
            'depends_on: mock_dep1, mock_dep2%(ls)s'
            'exception_details: sentinel.exception_details%(ls)s'
            'progress_updates:' % {"ls": os.linesep}
        )

        result = self.migration._format_task(mock_task)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(migrations.MigrationDetailFormatter, '_format_task')
    def test_format_tasks(self, mock_format_task):
        obj = mock.Mock()
        obj.tasks = [mock.sentinel.task1, mock.sentinel.task2]
        mock_format_task.side_effect = ["task1", "task2"]
        expected_result = 'task1%(ls)s%(ls)stask2' % {"ls": os.linesep}

        result = self.migration._format_tasks(obj)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(migrations.MigrationDetailFormatter, '_format_tasks')
    @mock.patch.object(cli_utils, 'format_mapping')
    @mock.patch.object(cli_utils, 'format_json_for_object_property')
    @mock.patch.object(migrations.MigrationDetailFormatter,
                       '_format_instances')
    @mock.patch.object(cli_utils, 'parse_storage_mappings')
    def test_get_formatted_data(
        self,
        mock_parse_storage_mappings,
        mock_format_instances,
        mock_format_json_for_object_property,
        mock_format_mapping,
        mock_format_tasks
    ):
        mock_obj = mock.Mock()
        obj = {
            "storage_mappings": {'default_storage': mock.sentinel.storage}
        }
        mock_obj.to_dict.return_value = obj
        mock_obj.id = mock.sentinel.id
        mock_obj.last_execution_status = mock.sentinel.last_execution_status
        mock_obj.created_at = mock.sentinel.created_at
        mock_obj.updated_at = mock.sentinel.updated_at
        mock_obj.reservation_id = mock.sentinel.reservation_id
        mock_format_instances.return_value = mock.sentinel.formatted_instances
        mock_obj.notes = mock.sentinel.notes
        mock_obj.origin_endpoint_id = mock.sentinel.origin_endpoint_id
        mock_obj.origin_minion_pool_id = mock.sentinel.origin_minion_pool_id
        mock_obj.destination_endpoint_id = \
            mock.sentinel.destination_endpoint_id
        mock_obj.destination_minion_pool_id = \
            mock.sentinel.destination_minion_pool_id
        mock_obj.replication_count = mock.sentinel.replication_count
        mock_obj.shutdown_instances = mock.sentinel.shutdown_instances
        mock_parse_storage_mappings.return_value = (
            mock.sentinel.default_storage,
            mock.sentinel.backend_mappings,
            mock.sentinel.disk_mappings
        )
        mock_format_json_for_object_property.side_effect = [
            mock.sentinel.instance_osmorphing_minion_pool_mappings,
            mock.sentinel.destination_environment,
            mock.sentinel.source_environment,
            mock.sentinel.network_map,
            mock.sentinel.user_scripts,
            mock.sentinel.transfer_result,
        ]
        mock_format_mapping.side_effect = [
            mock.sentinel.disk_mapping, mock.sentinel.backend_mappings]
        mock_format_tasks.return_value = mock.sentinel.formatted_tasks
        mock_obj.info = mock.sentinel.info
        expected_result = [
            mock.sentinel.id,
            mock.sentinel.last_execution_status,
            mock.sentinel.created_at,
            mock.sentinel.updated_at,
            mock.sentinel.reservation_id,
            mock.sentinel.formatted_instances,
            mock.sentinel.notes,
            mock.sentinel.origin_endpoint_id,
            mock.sentinel.origin_minion_pool_id,
            mock.sentinel.destination_endpoint_id,
            mock.sentinel.destination_minion_pool_id,
            mock.sentinel.instance_osmorphing_minion_pool_mappings,
            mock.sentinel.replication_count,
            mock.sentinel.shutdown_instances,
            mock.sentinel.destination_environment,
            mock.sentinel.source_environment,
            mock.sentinel.network_map,
            mock.sentinel.disk_mapping,
            mock.sentinel.backend_mappings,
            mock.sentinel.default_storage,
            mock.sentinel.user_scripts,
            mock.sentinel.formatted_tasks,
            mock.sentinel.transfer_result,
            mock.sentinel.info
        ]

        result = self.migration._get_formatted_data(mock_obj)

        self.assertEqual(
            expected_result,
            result
        )


class CreateMigrationTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Create Migration."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CreateMigrationTestCase, self).setUp()
        self.migration = migrations.CreateMigration(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(cli_utils, 'add_args_for_json_option_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        *_
    ):
        result = self.migration.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(cli_utils, 'compose_user_scripts')
    @mock.patch.object(cli_utils, 'get_storage_mappings_dict_from_args')
    @mock.patch.object(cli_utils, 'get_option_value_from_args')
    @mock.patch.object(migrations.MigrationDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity,
        mock_get_option_value_from_args,
        mock_get_storage_mappings_dict_from_args,
        mock_compose_user_scripts
    ):
        args = mock.Mock()
        args.instances = mock.sentinel.instances
        args.notes = mock.sentinel.notes
        args.skip_os_morphing = mock.sentinel.skip_os_morphing
        args.replication_count = mock.sentinel.replication_count
        args.shutdown_instances = mock.sentinel.shutdown_instances
        args.origin_minion_pool_id = mock.sentinel.origin_minion_pool_id
        args.destination_minion_pool_id = \
            mock.sentinel.destination_minion_pool_id
        args.instance_osmorphing_minion_pool_mappings = [
            {'instance_id': "instance_id1", 'pool_id': "pool_id1"},
            {'instance_id': "instance_id2", 'pool_id': "pool_id2"}
        ]
        mock_endpoints = mock.Mock()
        mock_migrations = mock.Mock()
        self.mock_app.client_manager.coriolis.endpoints = mock_endpoints
        mock_endpoints.get_endpoint_id_for_name.side_effect = [
            mock.sentinel.origin_endpoint_id,
            mock.sentinel.destination_endpoint_id
        ]
        self.mock_app.client_manager.coriolis.migrations.create = \
            mock_migrations
        mock_get_option_value_from_args.side_effect = [
            mock.sentinel.destination_environment,
            mock.sentinel.source_environment,
            mock.sentinel.network_map,
        ]

        result = self.migration.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_migrations.assert_called_once_with(
            mock.sentinel.origin_endpoint_id,
            mock.sentinel.destination_endpoint_id,
            mock.sentinel.source_environment,
            mock.sentinel.destination_environment,
            mock.sentinel.instances,
            network_map=mock.sentinel.network_map,
            notes=mock.sentinel.notes,
            storage_mappings=(mock_get_storage_mappings_dict_from_args.
                              return_value),
            skip_os_morphing=mock.sentinel.skip_os_morphing,
            replication_count=mock.sentinel.replication_count,
            shutdown_instances=mock.sentinel.shutdown_instances,
            origin_minion_pool_id=mock.sentinel.origin_minion_pool_id,
            destination_minion_pool_id=
            mock.sentinel.destination_minion_pool_id,
            instance_osmorphing_minion_pool_mappings={
                'instance_id1': 'pool_id1', 'instance_id2': 'pool_id2'},
            user_scripts=mock_compose_user_scripts.return_value
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_migrations.return_value)


class CreateMigrationFromReplicaTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Create Migration From Replica."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CreateMigrationFromReplicaTestCase, self).setUp()
        self.migration = migrations.CreateMigrationFromReplica(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(cli_utils, 'add_args_for_json_option_to_parser')
    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(
        self,
        mock_get_parser,
        *_
    ):
        result = self.migration.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(cli_utils, 'compose_user_scripts')
    @mock.patch.object(migrations.MigrationDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(
        self,
        mock_get_formatted_entity,
        mock_compose_user_scripts
    ):
        args = mock.Mock()
        args.replica = mock.sentinel.replica
        args.clone_disks = mock.sentinel.clone_disks
        args.force = mock.sentinel.force
        args.skip_os_morphing = mock.sentinel.skip_os_morphing
        args.instance_osmorphing_minion_pool_mappings = [
            {'instance_id': "instance_id1", 'pool_id': "pool_id1"},
            {'instance_id': "instance_id2", 'pool_id': "pool_id2"}
        ]
        mock_migrations = mock.Mock()
        self.mock_app.client_manager.coriolis.migrations = mock_migrations

        result = self.migration.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_migrations.create_from_replica.assert_called_once_with(
            mock.sentinel.replica,
            mock.sentinel.clone_disks,
            mock.sentinel.force,
            mock.sentinel.skip_os_morphing,
            user_scripts=mock_compose_user_scripts.return_value,
            instance_osmorphing_minion_pool_mappings={
                'instance_id1': 'pool_id1', 'instance_id2': 'pool_id2'}
        )
        mock_get_formatted_entity.assert_called_once_with(
            mock_migrations.create_from_replica.return_value)


class ShowMigrationTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Show Migration."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ShowMigrationTestCase, self).setUp()
        self.migration = migrations.ShowMigration(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(show.ShowOne, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.migration.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(migrations.MigrationDetailFormatter,
                       'get_formatted_entity')
    def test_take_action(self, mock_get_formatted_entity):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_migration = mock.Mock()
        self.mock_app.client_manager.coriolis.migrations.get = mock_migration

        result = self.migration.take_action(args)

        self.assertEqual(
            mock_get_formatted_entity.return_value,
            result
        )
        mock_migration.assert_called_once_with(mock.sentinel.id)
        mock_get_formatted_entity.assert_called_once_with(
            mock_migration.return_value)


class CancelMigrationTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Cancel Migration."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(CancelMigrationTestCase, self).setUp()
        self.migration = migrations.CancelMigration(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.migration.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.id = mock.sentinel.id
        args.force = mock.sentinel.force
        mock_migration = mock.Mock()
        self.mock_app.client_manager.coriolis.migrations.cancel = \
            mock_migration

        self.migration.take_action(args)

        mock_migration.assert_called_once_with(
            mock.sentinel.id, mock.sentinel.force)


class DeleteMigrationTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Delete Migration."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(DeleteMigrationTestCase, self).setUp()
        self.migration = migrations.DeleteMigration(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(command.Command, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.migration.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    def test_take_action(self):
        args = mock.Mock()
        args.id = mock.sentinel.id
        mock_migration = mock.Mock()
        self.mock_app.client_manager.coriolis.migrations.delete = \
            mock_migration

        self.migration.take_action(args)

        mock_migration.assert_called_once_with(mock.sentinel.id)


class ListMigrationTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Client List Migration."""

    def setUp(self):
        self.mock_app = mock.Mock()
        super(ListMigrationTestCase, self).setUp()
        self.migration = migrations.ListMigration(
            self.mock_app, mock.sentinel.app_args)

    @mock.patch.object(lister.Lister, 'get_parser')
    def test_get_parser(self, mock_get_parser):
        result = self.migration.get_parser(mock.sentinel.prog_name)

        self.assertEqual(
            mock_get_parser.return_value,
            result
        )
        mock_get_parser.assert_called_once_with(mock.sentinel.prog_name)

    @mock.patch.object(migrations.MigrationFormatter, 'list_objects')
    def test_take_action(self, mock_list_objects):
        args = mock.Mock()
        mock_migration = mock.Mock()
        self.mock_app.client_manager.coriolis.migrations.list = \
            mock_migration

        result = self.migration.take_action(args)

        self.assertEqual(
            mock_list_objects.return_value,
            result
        )
        mock_list_objects.assert_called_once_with(mock_migration.return_value)

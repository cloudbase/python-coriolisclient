# Copyright (c) 2024 Cloudbase Solutions Srl
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import copy
import os
from unittest import mock

from coriolisclient.cli import deployments
from coriolisclient.tests import test_base
from coriolisclient.v1 import common
from coriolisclient.v1 import deployments as v1_deployments

DEPLOYMENT_ID = "depl_id"
DEPLOYMENT_DATA = {
    "storage_mappings": None,
    "id": DEPLOYMENT_ID,
    "last_execution_status": "COMPLETED",
    "created_at": None,
    "updated_at": None,
    "transfer_id": "transfer_1",
    "transfer_scenario_type": "replica",
    "reservation_id": "res1",
    "instances": ["instance1"],
    "notes": "",
    "origin_endpoint_id": "source1",
    "origin_minion_pool_id": None,
    "destination_endpoint_id": "dest1",
    "destination_minion_pool_id": None,
    "instance_osmorphing_minion_pool_mappings": None,
    "shutdown_instances": False,
    "destination_environment": {"opt1": "env1"},
    "source_environment": None,
    "network_map": {"net_source": "net_dest"},
    "user_scripts": None,
    "tasks": [],
    "transfer_result": None,
}
DEPLOYMENT_FORMATTED_DATA = [
    "depl_id", "COMPLETED", None, None, "transfer_1", "replica", "res1",
    "instance1", "", "source1", None, "dest1", None, '{}', False,
    '{\n  "opt1": "env1"\n}', '{}', '{\n  "net_source": "net_dest"\n}', "", "",
    None, '{}', "", '{}']

DEPLOYMENT_LIST_DATA = {
    "id": "1",
    "transfer_id": "2",
    "last_execution_status": "RUNNING",
    "instances": ["instance1", "instance2"],
    "notes": "test_notes",
    "created_at": "2024-11-28T15:18:25.000000",
}
DEPLOYMENT_LIST_FORMATTED_DATA = (
    "1", "2", "RUNNING", "instance1\ninstance2", "test_notes",
    "2024-11-28T15:18:25.000000")
APP_MOCK = mock.MagicMock()


class DeploymentFormatterTestCase(test_base.CoriolisBaseTestCase):

    def setUp(self):
        super(DeploymentFormatterTestCase, self).setUp()
        self.formatter = deployments.DeploymentFormatter()

    def test__get_sorted_list(self):
        obj1 = mock.Mock(created_at="2024-10-24T18:51:32.000000")
        obj2 = mock.Mock(created_at="2024-11-18T15:18:25.000000")
        obj3 = mock.Mock(created_at="2024-11-28T15:18:25.000000")
        obj_list = [obj1, obj3, obj2]
        self.assertEqual(
            [obj1, obj2, obj3], self.formatter._get_sorted_list(obj_list))

    def test__get_formatted_data(self):
        obj = mock.Mock(**DEPLOYMENT_LIST_DATA)
        self.assertEqual(
            DEPLOYMENT_LIST_FORMATTED_DATA,
            self.formatter._get_formatted_data(obj))


class DeploymentDetailFormatterTestCase(test_base.CoriolisBaseTestCase):

    def setUp(self):
        super(DeploymentDetailFormatterTestCase, self).setUp()
        self.formatter = deployments.DeploymentDetailFormatter(
            show_instances_data=True)
        self.progress_updates = [
            {"created_at": "2024-10-24T18:51:32.000000",
             "index": 0,
             "message": "message 0"},
            {"created_at": "2024-11-18T15:18:25.000000",
             "index": 2,
             "message": "message 2"},
            {"created_at": "2024-11-28T15:18:25.000000",
             "index": 1,
             "message": "message 1"},
        ]
        self.formatted_progress_updates = (
            f"2024-10-24T18:51:32.000000 message 0{os.linesep}"
            f"2024-11-28T15:18:25.000000 message 1{os.linesep}"
            f"2024-11-18T15:18:25.000000 message 2")
        self.tasks_data = [
            {
                "id": "1",
                "task_type": "type1",
                "instance": "instance1",
                "status": "COMPLETED",
                "depends_on": ["task0"],
                "exception_details": None,
                "progress_updates": self.progress_updates,
            },
            {
                "id": "2",
                "task_type": "type2",
                "instance": "instance1",
                "status": "COMPLETED",
                "depends_on": ["task0"],
                "exception_details": None,
                "progress_updates": self.progress_updates,
            }
        ]
        self.formatted_tasks = [
            f'id: 1{os.linesep}'
            f'task_type: type1{os.linesep}'
            f'instance: instance1{os.linesep}'
            f'status: COMPLETED{os.linesep}'
            f'depends_on: task0{os.linesep}'
            f'exception_details: {os.linesep}'
            f'progress_updates:{os.linesep}'
            f'{self.formatted_progress_updates}',

            f'id: 2{os.linesep}'
            f'task_type: type2{os.linesep}'
            f'instance: instance1{os.linesep}'
            f'status: COMPLETED{os.linesep}'
            f'depends_on: task0{os.linesep}'
            f'exception_details: {os.linesep}'
            f'progress_updates:{os.linesep}'
            f'{self.formatted_progress_updates}'
        ]
        self.manager_mock = mock.MagicMock()

    def test_init_no_instances_data(self):
        formatter = deployments.DeploymentDetailFormatter(
            show_instances_data=False)
        self.assertNotIn('instances_data', formatter.columns)

    def test__format_instances(self):
        obj = mock.Mock(instances=["instance2", "instance3", "instance1"])
        self.assertEqual(
            f"instance1{os.linesep}instance2{os.linesep}instance3",
            self.formatter._format_instances(obj))

    def test__format_progress_updates(self):
        task_dict = {
            "progress_updates": self.progress_updates}
        self.assertEqual(
            self.formatted_progress_updates,
            self.formatter._format_progress_updates(task_dict))

    def test__format_task(self):
        task_data = self.tasks_data[0]

        task = common.Task(self.manager_mock, task_data)

        self.assertEqual(
            self.formatted_tasks[0], self.formatter._format_task(task))

    def test__format_tasks(self):
        obj = mock.Mock(
            tasks=[common.Task(self.manager_mock, task_data)
                   for task_data in self.tasks_data])
        expected_result = (f'{self.formatted_tasks[0]}{os.linesep}{os.linesep}'
                           f'{self.formatted_tasks[1]}')
        self.assertEqual(expected_result, self.formatter._format_tasks(obj))

    def test__get_formatted_data(self):
        obj_data = {
            **DEPLOYMENT_DATA,
            "info": {"depl": "info"},
        }
        obj = mock.Mock(**obj_data)
        obj.to_dict.return_value = obj_data
        expected_result = copy.copy(DEPLOYMENT_FORMATTED_DATA)
        expected_result.append(obj_data['info'])

        self.assertEqual(
            expected_result, self.formatter._get_formatted_data(obj))


class CreateDeploymentTestCase(test_base.CoriolisBaseTestCase):

    def setUp(self):
        super(CreateDeploymentTestCase, self).setUp()
        self.mock_app = APP_MOCK
        self.cli = deployments.CreateDeployment(self.mock_app, 'app_arg')

    def test_get_parser(self):
        parser = self.cli.get_parser('coriolis')
        global_script = "linux=/linux/path"
        instance_script = "instance1=/instance1/path"
        args = parser.parse_args([
            'transfer_id', '--force', '--dont-clone-disks',
            '--skip-os-morphing', '--user-script-global', global_script,
            '--user-script-instance', instance_script])
        self.assertEqual(
            ('transfer_id', True, False, True, [global_script],
             [instance_script]),
            (args.transfer, args.force, args.clone_disks,
             args.skip_os_morphing, args.global_scripts,
             args.instance_scripts))

    def test_take_action(self):
        args = mock.Mock(global_scripts=None, instance_scripts=None)
        args.instance_osmorphing_minion_pool_mappings = [
            {"instance_id": "instance1", "pool_id": "pool1"}]
        mock_fun = (self.mock_app.client_manager.coriolis.deployments.
                    create_from_transfer)
        mock_fun.return_value = (
            v1_deployments.Deployment(mock.MagicMock(), DEPLOYMENT_DATA))
        expected_pool_mappings = {"instance1": "pool1"}
        expected_user_scripts = {"global": {}, "instances": {}}
        expected_data = copy.copy(DEPLOYMENT_FORMATTED_DATA)

        columns, data = self.cli.take_action(args)

        self.assertEqual(
            deployments.DeploymentDetailFormatter().columns, columns)
        self.assertEqual(expected_data, data)
        mock_fun.assert_called_once_with(
            args.transfer, args.clone_disks, args.force, args.skip_os_morphing,
            user_scripts=expected_user_scripts,
            instance_osmorphing_minion_pool_mappings=expected_pool_mappings)


class ShowDeploymentTestCase(test_base.CoriolisBaseTestCase):

    def setUp(self):
        super(ShowDeploymentTestCase, self).setUp()
        self.mock_app = APP_MOCK
        self.cli = deployments.ShowDeployment(self.mock_app, 'app_args')

    def test_get_parser(self):
        parser = self.cli.get_parser('coriolis')
        args = parser.parse_args([DEPLOYMENT_ID, '--show-instances-data'])
        self.assertEqual(
            (DEPLOYMENT_ID, True),
            (args.id, args.show_instances_data))

    def test_take_action(self):
        show_instances_data = False
        args = mock.Mock(
            id=DEPLOYMENT_ID, show_instances_data=show_instances_data)
        mock_fun = self.mock_app.client_manager.coriolis.deployments.get
        mock_fun.return_value = v1_deployments.Deployment(
            mock.MagicMock(), DEPLOYMENT_DATA)
        expected_data = DEPLOYMENT_FORMATTED_DATA

        columns, data = self.cli.take_action(args)

        self.assertEqual(
            deployments.DeploymentDetailFormatter(
                show_instances_data=show_instances_data).columns, columns)
        self.assertEqual(expected_data, data)
        mock_fun.assert_called_once_with(DEPLOYMENT_ID)


class CancelDeploymentTestCase(test_base.CoriolisBaseTestCase):

    def setUp(self):
        super(CancelDeploymentTestCase, self).setUp()
        self.mock_app = APP_MOCK
        self.cli = deployments.CancelDeployment(self.mock_app, 'app_args')

    def test_get_parser(self):
        parser = self.cli.get_parser('coriolis')
        args = parser.parse_args([DEPLOYMENT_ID, '--force'])
        self.assertEqual((DEPLOYMENT_ID, True), (args.id, args.force))

    def test_take_action(self):
        force = True
        args = mock.Mock(id=DEPLOYMENT_ID, force=force)
        mock_fun = self.mock_app.client_manager.coriolis.deployments.cancel

        self.cli.take_action(args)

        mock_fun.assert_called_once_with(DEPLOYMENT_ID, force)


class DeleteDeploymentTestCase(test_base.CoriolisBaseTestCase):

    def setUp(self):
        super(DeleteDeploymentTestCase, self).setUp()
        self.mock_app = APP_MOCK
        self.cli = deployments.DeleteDeployment(self.mock_app, 'app_args')

    def test_get_parser(self):
        parser = self.cli.get_parser('coriolis')
        args = parser.parse_args([DEPLOYMENT_ID])
        self.assertEqual(DEPLOYMENT_ID, args.id)

    def test_take_action(self):
        args = mock.Mock(id=DEPLOYMENT_ID)
        mock_fun = self.mock_app.client_manager.coriolis.deployments.delete

        self.cli.take_action(args)
        mock_fun.assert_called_once_with(DEPLOYMENT_ID)


class ListDeploymentTestCase(test_base.CoriolisBaseTestCase):

    def setUp(self):
        super(ListDeploymentTestCase, self).setUp()
        self.mock_app = APP_MOCK
        self.cli = deployments.ListDeployment(self.mock_app, 'app_args')

    def test_get_parser(self):
        parser = self.cli.get_parser('coriolis')
        self.assertIsInstance(parser, argparse.ArgumentParser)

    def test_take_action(self):
        mock_fun = self.mock_app.client_manager.coriolis.deployments.list
        mock_fun.return_value = [
            v1_deployments.Deployment(mock.MagicMock(), DEPLOYMENT_LIST_DATA)]

        columns, data = self.cli.take_action(mock.ANY)

        self.assertEqual(deployments.DeploymentFormatter().columns, columns)
        self.assertEqual([DEPLOYMENT_LIST_FORMATTED_DATA], list(data))

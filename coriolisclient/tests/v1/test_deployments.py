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

from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import common
from coriolisclient.v1 import deployments

DEPLOYMENT_ID = "1"


class DeploymentResourceTestCase(test_base.CoriolisBaseTestCase):

    def setUp(self):
        super(DeploymentResourceTestCase, self).setUp()
        self.source_env = {"source_opt": "env_value"}
        self.dest_env = {"dest_opt": "env_value"}
        self.transfer_result = {"result": "value"}
        self.task = {"task": "type_1"}
        self.info = {
            "source_environment": self.source_env,
            "destination_environment": self.dest_env,
            "transfer_result": self.transfer_result,
            "tasks": [self.task],
        }
        self.deployment = deployments.Deployment(None, self.info)

    def test_source_environment(self):
        result = self.deployment.source_environment

        self.assertIsInstance(result, common.SourceEnvironment)
        self.assertEqual(self.source_env, result._info)

    def test_destination_environment(self):
        result = self.deployment.destination_environment

        self.assertIsInstance(result, common.DestinationEnvironment)
        self.assertEqual(self.dest_env, result._info)

    def test_transfer_result(self):
        result = self.deployment.transfer_result

        self.assertIsInstance(result, common.TransferResult)
        self.assertEqual(self.transfer_result, result._info)

    def test_task(self):
        result = self.deployment.tasks

        [self.assertIsInstance(t, common.Task) for t in result]
        self.assertEqual(self.task, result[0]._info)


class DeploymentManagerTestCase(test_base.CoriolisBaseTestCase):

    def setUp(self):
        super(DeploymentManagerTestCase, self).setUp()
        mock_client = mock.Mock()
        self.deployments = deployments.DeploymentManager(mock_client)

    def test_list(self):
        with mock.patch.object(self.deployments, '_list') as mock_list:
            result = self.deployments.list(detail=True)
            self.assertEqual(mock_list.return_value, result)
            mock_list.assert_called_once_with(
                '/deployments/detail', 'deployments')

    def test_get(self):
        deployment = mock.Mock(uuid=DEPLOYMENT_ID)
        with mock.patch.object(self.deployments, '_get') as mock_get:
            result = self.deployments.get(deployment)
            self.assertEqual(mock_get.return_value, result)
            mock_get.assert_called_once_with(
                f'/deployments/{DEPLOYMENT_ID}', 'deployment')

    def test_create_from_transfer(self):
        with mock.patch.object(self.deployments, '_post') as mock_post:
            expected_data = {
                "deployment": {
                    "transfer_id": mock.sentinel.transfer_id,
                    "clone_disks": True,
                    "force": False,
                    "skip_os_morphing": False,
                    "user_scripts": None,
                    "instance_osmorphing_minion_pool_mappings":
                        mock.sentinel.pool_mappings,
                }
            }
            result = self.deployments.create_from_transfer(
                mock.sentinel.transfer_id, clone_disks=True, force=False,
                skip_os_morphing=False, user_scripts=None,
                instance_osmorphing_minion_pool_mappings=(
                    mock.sentinel.pool_mappings))
            self.assertEqual(mock_post.return_value, result)
            mock_post.assert_called_once_with(
                "/deployments", expected_data, "deployment")

    def test_delete(self):
        with mock.patch.object(self.deployments, '_delete') as mock_delete:
            result = self.deployments.delete(DEPLOYMENT_ID)
            self.assertEqual(mock_delete.return_value, result)
            mock_delete.assert_called_once_with(
                f'/deployments/{DEPLOYMENT_ID}')

    def test_cancel(self):
        force = False
        expected_data = {"cancel": {"force": force}}
        with mock.patch.object(self.deployments.client, 'post') as mock_post:
            result = self.deployments.cancel(DEPLOYMENT_ID, force=force)
            self.assertEqual(mock_post.return_value, result)
            mock_post.assert_called_once_with(
                f"/deployments/{DEPLOYMENT_ID}/actions", json=expected_data)

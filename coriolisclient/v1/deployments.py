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

from coriolisclient import base
from coriolisclient.v1 import common


class Deployment(base.Resource):
    _tasks = None

    @property
    def source_environment(self):
        source_env = self._info.get("source_environment")
        if source_env is not None:
            return common.SourceEnvironment(None, source_env, loaded=True)

    @property
    def destination_environment(self):
        dest_env = self._info.get("destination_environment")
        if dest_env is not None:
            return common.DestinationEnvironment(None, dest_env, loaded=True)

    @property
    def transfer_result(self):
        res = self._info.get("transfer_result")
        if res is not None:
            return common.TransferResult(None, res, loaded=True)

    @property
    def tasks(self):
        if self._info.get('tasks') is None:
            self.get()
        return [common.Task(None, d, loaded=True) for d in
                self._info.get('tasks', [])]


class DeploymentManager(base.BaseManager):
    resource_class = Deployment

    def __init__(self, api):
        super(DeploymentManager, self).__init__(api)

    def list(self, detail=False):
        path = "/deployments"
        if detail:
            path = "%s/detail" % path
        return self._list(path, 'deployments')

    def get(self, deployment):
        return self._get(
            '/deployments/%s' % base.getid(deployment), 'deployment')

    def create_from_transfer(self, transfer_id, clone_disks=True, force=False,
                             skip_os_morphing=False, user_scripts=None,
                             instance_osmorphing_minion_pool_mappings=None):
        data = {
            "deployment": {
                "transfer_id": transfer_id,
                "clone_disks": clone_disks,
                "force": force,
                "skip_os_morphing": skip_os_morphing,
                "user_scripts": user_scripts}}
        if instance_osmorphing_minion_pool_mappings is not None:
            data['deployment']['instance_osmorphing_minion_pool_mappings'] = (
                instance_osmorphing_minion_pool_mappings)
        return self._post('/deployments', data, 'deployment')

    def delete(self, deployment):
        return self._delete('/deployments/%s' % base.getid(deployment))

    def cancel(self, deployment, force=False):
        return self.client.post(
            '/deployments/%s/actions' % base.getid(deployment),
            json={'cancel': {'force': force}})

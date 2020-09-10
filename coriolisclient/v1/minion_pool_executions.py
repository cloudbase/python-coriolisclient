# Copyright (c) 2016 Cloudbase Solutions Srl
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


class MinionPoolExecution(base.Resource):
    _tasks = None

    @property
    def tasks(self):
        if self._info.get('tasks') is None:
            self.manager.get(self._info.get("action_id"), self.id)
        return [common.Task(None, d, loaded=True) for d in
                self._info.get('tasks', [])]


class MinionPoolExecutionManager(base.BaseManager):
    resource_class = MinionPoolExecution

    def __init__(self, api):
        super(MinionPoolExecutionManager, self).__init__(api)

    def list(self, minion_pool):
        return self._list(
            '/minion_pools/%s/executions' % base.getid(minion_pool),
            'executions')

    def get(self, minion_pool, execution):
        return self._get(
            '/minion_pools/%(minion_pool_id)s/executions/%(execution_id)s' %
            {"minion_pool_id": base.getid(minion_pool),
             "execution_id": base.getid(execution)},
            'execution')

    def create(self, minion_pool, shutdown_instances=False):
        data = {"execution": {"shutdown_instances": shutdown_instances}}
        return self._post(
            '/minion_pools/%s/executions' % base.getid(minion_pool), data,
            'execution')

    def delete(self, minion_pool, execution):
        return self._delete(
            '/minion_pools/%(minion_pool_id)s/executions/%(execution_id)s' %
            {"minion_pool_id": base.getid(minion_pool),
             "execution_id": base.getid(execution)})

    def cancel(self, minion_pool, execution, force=False):
        return self.client.post(
            '/minion_pools/%(minion_pool_id)s/executions'
            '/%(execution_id)s/actions' %
            {"minion_pool_id": base.getid(minion_pool),
             "execution_id": base.getid(execution)},
            json={'cancel': {'force': force}})

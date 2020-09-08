# Copyright (c) 2020 Cloudbase Solutions Srl
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
from coriolisclient.v1 import minion_pool_executions


class MinionPool(base.Resource):
    pass


class MinionPoolManager(base.BaseManager):
    resource_class = MinionPool

    def __init__(self, api):
        super(MinionPoolManager, self).__init__(api)

    def list(self):
        return self._list('/minion_pools', 'minion_pools')

    def get(self, minion_pool):
        return self._get(
            '/minion_pools/%s' % base.getid(minion_pool), 'minion_pool')

    def create(
            self, name, endpoint, pool_platform, pool_os_type,
            environment_options,
            minimum_minions=None, maximum_minions=None,
            minion_max_idle_time=None, minion_retention_strategy=None,
            notes=None):
        data = {
            "pool_name": name,
            "pool_platform": pool_platform,
            "pool_os_type": pool_os_type,
            "endpoint_id": base.getid(endpoint),
            "environment_options": environment_options}
        if minimum_minions is not None:
            data['minimum_minions'] = minimum_minions
        if maximum_minions is not None:
            data['maximum_minions'] = maximum_minions
        if minion_max_idle_time is not None:
            data['minion_max_idle_time'] = minion_max_idle_time
        if minion_retention_strategy is not None:
            data['minion_retention_strategy'] = minion_retention_strategy
        if notes:
            data['notes'] = notes

        return self._post('/minion_pools', {'minion_pool': data}, 'minion_pool')

    def update(self, minion_pool, updated_values):
        data = {
            "minion_pool": updated_values
        }
        return self._put(
            '/minion_pools/%s' % base.getid(minion_pool), data, 'minion_pool')

    def delete(self, minion_pool):
        return self._delete('/minion_pools/%s' % base.getid(minion_pool))

    def set_up_shared_resources(self, minion_pool):
        response = self.client.post(
            '/minion_pools/%s/actions' % base.getid(minion_pool),
            json={'set-up-shared-resources': None})

        return minion_pool_executions.MinionPoolExecution(
            self, response.json().get("execution"), loaded=True)

    def tear_down_shared_resources(self, minion_pool):
        response = self.client.post(
            '/minion_pools/%s/actions' % base.getid(minion_pool),
            json={'tear-down-shared-resources': None})

        return minion_pool_executions.MinionPoolExecution(
            self, response.json().get("execution"), loaded=True)

    def allocate_machines(self, minion_pool):
        response = self.client.post(
            '/minion_pools/%s/actions' % base.getid(minion_pool),
            json={'allocate-machines': None})

        return minion_pool_executions.MinionPoolExecution(
            self, response.json().get("execution"), loaded=True)

    def deallocate_machines(self, minion_pool):
        response = self.client.post(
            '/minion_pools/%s/actions' % base.getid(minion_pool),
            json={'deallocate-machines': None})

        return minion_pool_executions.MinionPoolExecution(
            self, response.json().get("execution"), loaded=True)

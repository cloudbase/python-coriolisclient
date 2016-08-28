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


class ReplicaExecution(base.Resource):
    _tasks = None

    @property
    def tasks(self):
        if self._info.get('tasks') is None:
            self.manager.get(self._info.get("action_id"), self.id)
        return [common.Task(None, d, loaded=True) for d in
                self._info.get('tasks', [])]


class ReplicaExecutionManager(base.BaseManager):
    resource_class = ReplicaExecution

    def __init__(self, api):
        super(ReplicaExecutionManager, self).__init__(api)

    def list(self, replica):
        return self._list(
            '/replicas/%s/executions' % base.getid(replica), 'executions')

    def get(self, replica, execution):
        return self._get(
            '/replicas/%(replica_id)s/executions/%(execution_id)s' %
            {"replica_id": base.getid(replica),
             "execution_id": base.getid(execution)},
            'execution')

    def create(self, replica, shutdown_instances=False):
        data = {"execution": {"shutdown_instances": shutdown_instances}}
        return self._post(
            '/replicas/%s/executions' % base.getid(replica), data, 'execution')

    def delete(self, replica, execution):
        return self._delete(
            '/replicas/%(replica_id)s/executions/%(execution_id)s' %
            {"replica_id": base.getid(replica),
             "execution_id": base.getid(execution)})

    def cancel(self, replica, execution, force=False):
        return self.client.post(
            '/replicas/%(replica_id)s/executions/%(execution_id)s/actions' %
            {"replica_id": base.getid(replica),
             "execution_id": base.getid(execution)},
            json={'cancel': {'force': force}})

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


class TransferExecution(base.Resource):
    _tasks = None

    @property
    def tasks(self):
        if self._info.get('tasks') is None:
            self.manager.get(self._info.get("action_id"), self.id)
        return [common.Task(None, d, loaded=True) for d in
                self._info.get('tasks', [])]


class TransferExecutionManager(base.BaseManager):
    resource_class = TransferExecution

    def __init__(self, api):
        super(TransferExecutionManager, self).__init__(api)

    def list(self, transfer):
        return self._list(
            '/transfers/%s/executions' % base.getid(transfer), 'executions')

    def get(self, transfer, execution):
        return self._get(
            '/transfers/%(transfer_id)s/executions/%(execution_id)s' %
            {"transfer_id": base.getid(transfer),
             "execution_id": base.getid(execution)},
            'execution')

    def create(self, transfer, shutdown_instances=False):
        data = {"execution": {"shutdown_instances": shutdown_instances}}
        return self._post(
            '/transfers/%s/executions' %
            base.getid(transfer), data, 'execution')

    def delete(self, transfer, execution):
        return self._delete(
            '/transfers/%(transfer_id)s/executions/%(execution_id)s' %
            {"transfer_id": base.getid(transfer),
             "execution_id": base.getid(execution)})

    def cancel(self, transfer, execution, force=False):
        return self.client.post(
            '/transfers/%(transfer_id)s/executions/%(execution_id)s/actions' %
            {"transfer_id": base.getid(transfer),
             "execution_id": base.getid(execution)},
            json={'cancel': {'force': force}})

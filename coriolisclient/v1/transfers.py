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
from coriolisclient.v1 import transfer_executions


class Transfer(base.Resource):
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
    def executions(self):
        if self._info.get('executions') is None:
            self.get()
        return [common.TasksExecution(None, d, loaded=True) for d in
                self._info.get('executions', [])]


class TransferManager(base.BaseManager):
    resource_class = Transfer

    def __init__(self, api):
        super(TransferManager, self).__init__(api)

    def list(self, detail=False):
        path = "/transfers"
        if detail:
            path = "%s/detail" % path
        return self._list(path, 'transfers')

    def get(self, transfer):
        return self._get('/transfers/%s' % base.getid(transfer), 'transfer')

    def create(self, origin_endpoint_id, destination_endpoint_id,
               source_environment, destination_environment, instances,
               transfer_scenario,
               network_map=None, notes=None, storage_mappings=None,
               origin_minion_pool_id=None, destination_minion_pool_id=None,
               instance_osmorphing_minion_pool_mappings=None,
               user_scripts=None, clone_disks=True, skip_os_morphing=False):
        if not network_map:
            network_map = destination_environment.get('network_map', {})
        if not storage_mappings:
            storage_mappings = destination_environment.get(
                'storage_mappings', {})
        data = {
            "transfer": {
                "origin_endpoint_id": origin_endpoint_id,
                "destination_endpoint_id": destination_endpoint_id,
                "destination_environment": destination_environment,
                "instances": instances,
                "scenario": transfer_scenario,
                "network_map": network_map,
                "notes": notes,
                "storage_mappings": storage_mappings,
                "user_scripts": user_scripts,
                "clone_disks": clone_disks,
                "skip_os_morphing": skip_os_morphing,
            }
        }
        if source_environment:
            data['transfer']['source_environment'] = source_environment
        if origin_minion_pool_id is not None:
            data['transfer']['origin_minion_pool_id'] = origin_minion_pool_id
        if destination_minion_pool_id is not None:
            data['transfer']['destination_minion_pool_id'] = (
                destination_minion_pool_id)
        if instance_osmorphing_minion_pool_mappings:
            data['transfer']['instance_osmorphing_minion_pool_mappings'] = (
                instance_osmorphing_minion_pool_mappings)

        return self._post('/transfers', data, 'transfer')

    def delete(self, transfer):
        return self._delete('/transfers/%s' % base.getid(transfer))

    def delete_disks(self, transfer):
        response = self.client.post(
            '/transfers/%s/actions' % base.getid(transfer),
            json={'delete-disks': None})

        return transfer_executions.TransferExecution(
            self, response.json().get("execution"), loaded=True)

    def update(self, transfer, updated_values):
        data = {
            "transfer": updated_values
        }
        response = self.client.put(
            '/transfers/%s' % base.getid(transfer), json=data)

        return transfer_executions.TransferExecution(
            self, response.json().get("execution"), loaded=True)

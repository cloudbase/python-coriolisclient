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
from coriolisclient.v1 import replica_executions


class Replica(base.Resource):
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


class ReplicaManager(base.BaseManager):
    resource_class = Replica

    def __init__(self, api):
        super(ReplicaManager, self).__init__(api)

    def list(self):
        return self._list('/replicas/detail', 'replicas')

    def get(self, replica):
        return self._get('/replicas/%s' % base.getid(replica), 'replica')

    def create(self, origin_endpoint_id, destination_endpoint_id,
               source_environment, destination_environment, instances,
               network_map=None, notes=None, storage_mappings=None,
               origin_minion_pool_id=None, destination_minion_pool_id=None,
               instance_osmorphing_minion_pool_mappings=None,
               user_scripts=None):
        if not network_map:
            network_map = destination_environment.get('network_map', {})
        if not storage_mappings:
            storage_mappings = destination_environment.get(
                'storage_mappings', {})
        data = {
            "replica": {
                "origin_endpoint_id": origin_endpoint_id,
                "destination_endpoint_id": destination_endpoint_id,
                "destination_environment": destination_environment,
                "instances": instances,
                "network_map": network_map,
                "notes": notes,
                "storage_mappings": storage_mappings,
                "user_scripts": user_scripts,
            }
        }
        if source_environment:
            data['replica']['source_environment'] = source_environment
        if origin_minion_pool_id is not None:
            data['replica']['origin_minion_pool_id'] = origin_minion_pool_id
        if destination_minion_pool_id is not None:
            data['replica']['destination_minion_pool_id'] = (
                destination_minion_pool_id)
        if instance_osmorphing_minion_pool_mappings:
            data['replica']['instance_osmorphing_minion_pool_mappings'] = (
                instance_osmorphing_minion_pool_mappings)

        return self._post('/replicas', data, 'replica')

    def delete(self, replica):
        return self._delete('/replicas/%s' % base.getid(replica))

    def delete_disks(self, replica):
        response = self.client.post(
            '/replicas/%s/actions' % base.getid(replica),
            json={'delete-disks': None})

        return replica_executions.ReplicaExecution(
            self, response.json().get("execution"), loaded=True)

    def update(self, replica, updated_values):
        data = {
            "replica": updated_values
        }
        response = self.client.put(
            '/replicas/%s' % base.getid(replica), json=data)

        return replica_executions.ReplicaExecution(
            self, response.json().get("execution"), loaded=True)

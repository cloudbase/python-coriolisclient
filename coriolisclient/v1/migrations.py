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


class Migration(base.Resource):
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


class MigrationManager(base.BaseManager):
    resource_class = Migration

    def __init__(self, api):
        super(MigrationManager, self).__init__(api)

    def list(self):
        return self._list('/migrations/detail', 'migrations')

    def get(self, migration):
        return self._get('/migrations/%s' % base.getid(migration), 'migration')

    def create(self, origin_endpoint_id, destination_endpoint_id,
               source_environment, destination_environment, instances,
               network_map=None, storage_mappings=None,
               skip_os_morphing=False, replication_count=None,
               shutdown_instances=None):
        if not network_map:
            network_map = destination_environment.get('network_map', {})
        if not storage_mappings:
            storage_mappings = destination_environment.get(
                'storage_mappings', {})

        data = {
            "migration": {
                "origin_endpoint_id": origin_endpoint_id,
                "destination_endpoint_id": destination_endpoint_id,
                "destination_environment": destination_environment,
                "instances": instances,
                "skip_os_morphing": skip_os_morphing,
                "network_map": network_map,
                "storage_mappings": storage_mappings}}
        if source_environment is not None:
            data['migration']['source_environment'] = source_environment
        if shutdown_instances is not None:
            data['migration']['shutdown_instances'] = shutdown_instances
        if replication_count is not None:
            data['migration']['replication_count'] = replication_count

        return self._post('/migrations', data, 'migration')

    def create_from_replica(self, replica_id, clone_disks=True, force=False,
                            skip_os_morphing=False):
        data = {"migration": {
            "replica_id": replica_id,
            "clone_disks": clone_disks,
            "force": force,
            "skip_os_morphing": skip_os_morphing}}
        return self._post('/migrations', data, 'migration')

    def delete(self, migration):
        return self._delete('/migrations/%s' % base.getid(migration))

    def cancel(self, migration, force=False):
        return self.client.post(
            '/migrations/%s/actions' % base.getid(migration),
            json={'cancel': {'force': force}})

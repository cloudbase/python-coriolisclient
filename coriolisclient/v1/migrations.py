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
    def target_environment(self):
        dest_env = self._info.get("destination_environment")
        if dest_env is not None:
            return common.TargetEnvironment(None, dest_env, loaded=True)

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
               target_environment, instances):
        data = {"migration": {
            "origin_endpoint_id": origin_endpoint_id,
            "destination_endpoint_id": destination_endpoint_id,
            "destination_environment": target_environment,
            "instances": instances, }
        }
        return self._post('/migrations', data, 'migration')

    def create_from_replica(self, replica_id, clone_disks=True, force=False):
        data = {"migration": {
            "replica_id": replica_id,
            "clone_disks": clone_disks,
            "force": force}}
        return self._post('/migrations', data, 'migration')

    def delete(self, migration):
        return self._delete('/migrations/%s' % base.getid(migration))

    def cancel(self, migration, force=False):
        return self.client.post(
            '/migrations/%s/actions' % base.getid(migration),
            json={'cancel': {'force': force}})

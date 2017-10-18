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
import logging

from keystoneauth1 import adapter

from coriolisclient.v1 import endpoint_instances
from coriolisclient.v1 import endpoint_networks
from coriolisclient.v1 import endpoints
from coriolisclient.v1 import migrations
from coriolisclient.v1 import replica_executions
from coriolisclient.v1 import replica_schedules
from coriolisclient.v1 import replicas

LOG = logging.getLogger(__name__)

_DEFAULT_SERVICE_TYPE = 'migration'
_DEFAULT_SERVICE_INTERFACE = 'public'
_DEFAULT_API_VERSION = 'v1'


class _HTTPClient(adapter.Adapter):
    def __init__(self, session, project_id=None, **kwargs):
        kwargs.setdefault('interface', _DEFAULT_SERVICE_INTERFACE)
        kwargs.setdefault('service_type', _DEFAULT_SERVICE_TYPE)
        kwargs.setdefault('version', _DEFAULT_API_VERSION)
        endpoint = kwargs.pop('endpoint', None)

        super(_HTTPClient, self).__init__(session, **kwargs)

        if endpoint:
            self.endpoint_override = '{0}/{1}'.format(endpoint, self.version)


class Client(object):
    def __init__(self, session=None, *args, **kwargs):
        httpclient = _HTTPClient(session=session, *args, **kwargs)
        self.endpoints = endpoints.EndpointManager(httpclient)
        self.endpoint_instances = endpoint_instances.EndpointInstanceManager(
            httpclient)
        self.endpoint_networks = endpoint_networks.EndpointNetworkManager(
            httpclient)
        self.migrations = migrations.MigrationManager(httpclient)
        self.replicas = replicas.ReplicaManager(httpclient)
        self.replica_schedules = replica_schedules.ReplicaScheduleManager(
            httpclient)
        self.replica_executions = replica_executions.ReplicaExecutionManager(
            httpclient)

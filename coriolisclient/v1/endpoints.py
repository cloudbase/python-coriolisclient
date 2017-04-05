# Copyright (c) 2017 Cloudbase Solutions Srl
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


class ConnectionInfo(base.Resource):
    pass


class Endpoint(base.Resource):
    @property
    def connection_info(self):
        return ConnectionInfo(
            None, self._info.get("connection_info"), loaded=True)


class EndpointManager(base.BaseManager):
    resource_class = Endpoint

    def __init__(self, api):
        super(EndpointManager, self).__init__(api)

    def list(self):
        return self._list('/endpoints', 'endpoints')

    def get(self, endpoint):
        return self._get('/endpoints/%s' % base.getid(endpoint), 'endpoint')

    def create(self, name, endpoint_type, connection_info, description):
        data = {
            "endpoint": {
                "name": name,
                "type": endpoint_type,
                "description": description,
                "connection_info": connection_info,
            }
        }

        return self._post('/endpoints', data, 'endpoint')

    def delete(self, endpoint):
        return self._delete('/endpoints/%s' % base.getid(endpoint))

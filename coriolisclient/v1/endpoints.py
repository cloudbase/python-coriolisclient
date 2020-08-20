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
from coriolisclient import exceptions
from coriolisclient.cli import utils


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

    def create(
            self, name, endpoint_type, connection_info,
            description, regions):
        data = {
            "endpoint": {
                "name": name,
                "type": endpoint_type,
                "description": description,
                "connection_info": connection_info,
                "mapped_regions": regions}}

        return self._post('/endpoints', data, 'endpoint')

    def update(self, endpoint, updated_values):
        data = {
            "endpoint": updated_values
        }
        return self._put(
            '/endpoints/%s' % base.getid(endpoint), data, 'endpoint')

    def delete(self, endpoint):
        return self._delete('/endpoints/%s' % base.getid(endpoint))

    def validate_connection(self, endpoint):
        data = self.client.post(
            '/endpoints/%s/actions' % base.getid(endpoint),
            json={'validate-connection': None}).json()
        validate_data = data["validate-connection"]
        return validate_data.get("valid"), validate_data.get("message")

    def get_endpoint_id_for_name(self, endpoint):
        """ Gets the UUID of the endpoint from the parsed name """
        if utils.validate_uuid_string(endpoint):
            return endpoint
        else:
            return self._get_endpoint_id_for_name(endpoint)

    def _get_endpoint_id_for_name(self, endpoint_name):
        obj_list = self.list()
        id_matches = [n.id for n in obj_list if n.name == endpoint_name]
        matches = len(id_matches)
        if matches == 1:
            return id_matches[0]
        elif matches > 1:
            raise exceptions.NoUniqueEndpointNameMatch(endpoint_name)
        else:
            raise exceptions.EndpointIDNotFound(endpoint_name)

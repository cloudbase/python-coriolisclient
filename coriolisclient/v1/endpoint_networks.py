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
from coriolisclient.v1 import common


class EndpointNetwork(base.Resource):
    pass


class EndpointNetworkManager(base.BaseManager):
    resource_class = EndpointNetwork

    def __init__(self, api):
        super(EndpointNetworkManager, self).__init__(api)

    def list(self, endpoint, environment=None):
        url = '/endpoints/%s/networks' % base.getid(endpoint)

        if environment:
            encoded_env = common.encode_base64_param(environment, is_json=True)
            url = '%s?env=%s' % (url, encoded_env)

        return self._list(url, 'networks')

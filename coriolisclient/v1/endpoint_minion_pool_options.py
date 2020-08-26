# Copyright (c) 2020 Cloudbase Solutions Srl
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

import base64
import json

from coriolisclient import base


class EndpointMinionPoolOption(base.Resource):
    pass


class EndpointMinionPoolOptionsManager(base.BaseManager):
    resource_class = EndpointMinionPoolOption

    def __init__(self, api):
        super(EndpointMinionPoolOptionsManager, self).__init__(api)

    def list(self, endpoint, environment=None, option_names=None):
        url = '/endpoints/%s/minion-pool-options' % base.getid(endpoint)

        if environment:
            encoded_env = base64.b64encode(
                json.dumps(environment).encode()).decode()
            url = '%s?env=%s' % (url, encoded_env)

        if option_names:
            sep = "?"
            if environment:
                sep = "&"
            encoded_option_names = base64.b64encode(
                json.dumps(option_names).encode()).decode()
            url = '%s%soptions=%s' % (url, sep, encoded_option_names)

        return self._list(url, 'minion_pool_options')

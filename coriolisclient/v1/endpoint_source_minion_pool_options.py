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

from coriolisclient import base
from coriolisclient.v1 import common


class EndpointSourceMinionPoolOption(base.Resource):
    pass


class EndpointSourceMinionPoolOptionsManager(base.BaseManager):
    resource_class = EndpointSourceMinionPoolOption

    def __init__(self, api):
        super(EndpointSourceMinionPoolOptionsManager, self).__init__(api)

    def list(self, endpoint, environment=None, option_names=None):
        url = '/endpoints/%s/source-minion-pool-options' % base.getid(endpoint)

        if environment:
            encoded_env = common.encode_base64_param(environment, is_json=True)
            url = '%s?env=%s' % (url, encoded_env)

        if option_names:
            sep = "?"
            if environment:
                sep = "&"
            encoded_option_names = common.encode_base64_param(
                option_names, is_json=True)
            url = '%s%soptions=%s' % (url, sep, encoded_option_names)

        return self._list(url, 'source_minion_pool_options')

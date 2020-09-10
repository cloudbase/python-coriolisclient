# Copyright (c) 2018 Cloudbase Solutions Srl
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


class Providers(base.Resource):
    @property
    def providers_list(self):
        # NOTE: API returns dict with provider name as keys:
        providers_list = [
            {"name": k, "types": v["types"]}
            for (k, v) in self._info.items()]
        return providers_list

    @property
    def provider_schemas(self):
        schemas = [
            {"type": k,
             "schema": v}
            for (k, v) in self._info.items()]
        return schemas


class ProvidersManager(base.BaseManager):
    resource_class = Providers

    def __init__(self, api):
        super(ProvidersManager, self).__init__(api)

    def list(self):
        return self._get('/providers', 'providers')

    def schemas_list(self, provider_name, provider_type):
        url = '/providers/%s/schemas/%s' % (provider_name, provider_type)
        return self._get(url, 'schemas')

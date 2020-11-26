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
from coriolisclient.v1 import licensing


class Appliance(base.Resource):
    pass


class LicensingAppliancesManager(base.BaseManager):
    resource_class = Appliance

    def __init__(self, api):
        super().__init__(api)
        self._licensing_cli = licensing.LicensingClient(api)

    def list(self):
        url = '/appliances'
        data = self._licensing_cli._get(url, response_key='appliances')
        return [self.resource_class(self, app, loaded=True)
                for app in data if app]

    def show(self, appliance_id):
        url = '/appliances/%s' % appliance_id
        data = self._licensing_cli._get(url, response_key='appliance')
        return self.resource_class(self, data, loaded=True)

    def create(self):
        url = '/appliances'
        data = self._licensing_cli._post(url, response_key='apppliance')
        return self.resource_class(self, data, loaded=True)

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


class Reservation(base.Resource):
    pass


class LicensingReservationsManager(base.BaseManager):
    resource_class = Reservation

    def __init__(self, api):
        super().__init__(api)
        self._licensing_cli = licensing.LicensingClient(api)

    def list(self, appliance_id):
        url = '/appliances/%s/reservations' % appliance_id
        data = self._licensing_cli.get(url, response_key='reservations')
        return [self.resource_class(self, res, loaded=True)
                for res in data if res]

    def show(self, appliance_id, reservation_id):
        url = '/appliances/%s/reservations/%s' % (appliance_id, reservation_id)
        data = self._licensing_cli.get(url, response_key='reservation')
        return self.resource_class(self, data, loaded=True)

    def refresh(self, appliance_id, reservation_id):
        url = '/appliances/%s/reservations/%s/refresh' % (
            appliance_id, reservation_id)
        data = self._licensing_cli.post(url, response_key='reservation')
        return self.resource_class(self, data, loaded=True)

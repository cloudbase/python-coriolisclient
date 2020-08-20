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
from coriolisclient import exceptions
from coriolisclient.cli import utils


class Service(base.Resource):
    pass


class ServiceManager(base.BaseManager):
    resource_class = Service

    def __init__(self, api):
        super(ServiceManager, self).__init__(api)

    def list(self):
        return self._list('/services', 'services')

    def get(self, service):
        return self._get('/services/%s' % base.getid(service), 'service')

    def create(self, host, binary, topic, regions, enabled=True):
        data = {
            "service": {
                "host": host,
                "binary": binary,
                "topic": topic,
                "enabled": enabled,
                "mapped_regions": regions}}

        return self._post('/services', data, 'service')

    def update(self, service, updated_values):
        data = {
            "service": updated_values
        }
        return self._put(
            '/services/%s' % base.getid(service), data, 'service')

    def delete(self, service):
        return self._delete('/services/%s' % base.getid(service))

    def find_service_by_host_and_topic(self, host, topic):
        services = self.list()
        matches = [
            svc for svc in services
            if svc.host == host and svc.topic == topic]
        if not matches:
            raise ValueError(
                "No Service with the host/topic %s/%s was found." % (
                    host, topic))
        if len(matches) > 1:
            raise ValueError(
                "Multiple services with the host/topic %s/%s were found: %s" % (
                    host, topic, matches))

        return matches[0]

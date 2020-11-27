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

import json
import logging

import requests

from coriolisclient import base
from coriolisclient import exceptions

LOG = logging.getLogger(__name__)
_LICENSING_ENDPOINT_NAME = "coriolis-licensing"


class Licence(base.Resource):
    pass


class LicensingClient(object):

    def __init__(self, client, endpoint_name_override=None):
        self._cli = client
        self._endpoint_name = _LICENSING_ENDPOINT_NAME
        if endpoint_name_override:
            self._endpoint_name = endpoint_name_override

    def _get_licensing_endpoint_url(self):
        endpoint_url = None
        try:
            endpoint_url = self._cli.get_endpoint(
                service_type=self._endpoint_name)
        except Exception as ex:
            LOG.warning("Unable to determine licensing endpoint: %s", str(ex))
            raise exceptions.LicensingEndpointNotFound(self._endpoint_name)
        return endpoint_url.rstrip('/')

    def _do_req(self, method_name, resource, body=None, response_key=None,
                raw_response=False):
        method = getattr(requests, method_name.lower(), None)
        if not method:
            raise ValueError("No such HTTP method '%s'" % method_name)

        endpoint_url = self._get_licensing_endpoint_url()
        url = '%s/%s' % (endpoint_url.rstrip('/'), resource.lstrip('/'))

        kwargs = dict()
        if body:
            if not isinstance(body, (str, bytes)):
                body = json.dumps(body)
            kwargs["data"] = body

        resp = method(url, **kwargs)

        if not resp.ok:
            # try to extract error from licensing server:
            error = None
            try:
                error = resp.json().get('error', {})
            except (Exception, KeyboardInterrupt) as ex:
                LOG.debug(
                    "Exception occured during error extraction from licensing "
                    "response: '%s'\nException:\n%s",
                    resp.text, ex)
            if error and all([x in error for x in ['code', 'message']]):
                raise exceptions.HTTPError(
                    message=error['message'],
                    status_code=int(error['code']))
            else:
                resp.raise_for_status()

        if raw_response:
            return resp

        else:
            resp_data = resp.json()
            if response_key:
                if response_key not in resp_data:
                    raise ValueError(
                        'No response key "%s" in response body: %s' % (
                            response_key, resp_data))
                resp_data = resp_data[response_key]

        return resp_data

    def get(self, resource, body=None, response_key=None, raw_response=False):
        return self._do_req('GET', resource, response_key=response_key,
                            body=body, raw_response=raw_response)

    def post(self, resource, body=None, response_key=None,
              raw_response=False):
        return self._do_req(
            'POST', resource, body=body, response_key=response_key,
            raw_response=raw_response)

    def delete(self, resource, body=None, response_key=None,
                raw_response=False):
        return self._do_req('DELETE', resource, raw_response=raw_response,
                            body=body, response_key=response_key)


class LicensingManager(base.BaseManager):
    resource_class = Licence

    def __init__(self, api):
        super(LicensingManager, self).__init__(api)
        self._licensing_cli = LicensingClient(api)

    def status(self, appliance_id):
        url = '/appliances/%s/status' % appliance_id
        data = self._licensing_cli.get(
            url, response_key='appliance_licence_status')
        return self.resource_class(self, data, loaded=True)

    def list(self, appliance_id):
        url = '/appliances/%s/licences' % appliance_id
        data = self._licensing_cli.get(url, response_key='licences')
        return [self.resource_class(self, lic, loaded=True)
                for lic in data if lic]

    def register(self, appliance_id, licence):
        url = '/appliances/%s/licences' % appliance_id
        data = self._licensing_cli.post(
            url, body=licence, response_key='licence')
        return self.resource_class(self, data, loaded=True)

    def show(self, appliance_id, licence_id):
        url = '/appliances/%s/licences/%s' % (appliance_id, licence_id)
        data = self._licensing_cli.get(url, response_key='licence')
        return self.resource_class(self, data, loaded=True)

    def delete(self, appliance_id, licence_id):
        url = '/appliances/%s/licences/%s' % (appliance_id, licence_id)
        return self._licensing_cli.delete(url, raw_response=True)

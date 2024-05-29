# Copyright (c) 2019 Cloudbase Solutions Srl
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

import asyncio
import datetime
import json
import logging
import ssl
import traceback

import requests
import websockets

from keystoneauth1.exceptions import catalog
from keystoneauth1.exceptions import http
from six.moves.urllib import parse as urlparse

from coriolisclient import base
from coriolisclient import exceptions


LOG = logging.getLogger(__name__)
_LOGGING_ENDPOINT_NAME = "coriolis-logger"


class LoggingClient(object):

    def __init__(self, client, endpoint_name_override=None):
        self._cli = client
        self._ep_name = endpoint_name_override or _LOGGING_ENDPOINT_NAME
        self._ep_url = None
        try:
            self._ep_url = self._get_endpoint_url(self._ep_name)
        except Exception as ex:
            LOG.warning(
                "Unable to determine logging endpoint: %s", str(ex))

    @property
    def _token(self):
        return self._cli.get_token()

    def _get_endpoint_url(self, name):
        try:
            url = self._cli.get_endpoint(service_type=name)
            if url is None:
                raise catalog.EndpointNotFound()
            return url.rstrip("/")
        except catalog.EndpointNotFound:
            raise exceptions.LoggingEndpointNotFound()
        except http.Unauthorized as ex:
            LOG.exception(traceback.format_exc())
            raise exceptions.HTTPAuthError(
                "Failed to authorize Keystone session. Please recheck "
                "credentials. The error message received from Keystone was: "
                "%s" % str(ex))

    @property
    def _auth_headers(self):
        head = {
            "X-Auth-Token": self._token,
        }
        return head

    def _construct_url(self, resource, query_args={}, is_websocket=False):
        args = {}
        for i in query_args:
            if query_args[i] is None:
                continue
            args[i] = query_args[i]

        if not self._ep_url:
            self._ep_url = self._get_endpoint_url(self._ep_name)
        url = "%s/%s" % (self._ep_url, resource)
        if len(args):
            url += "?" + urlparse.urlencode(args)
        parsed = urlparse.urlparse(url)
        if is_websocket:
            wsScheme = "ws"
            if parsed.scheme == "https":
                wsScheme = "wss"
            newURL = parsed._replace(scheme=wsScheme)
            url = newURL.geturl()
        return url

    def stream_logs(self, app_name=None, severity=None):
        headers = self._auth_headers
        args = {
            "app_name": app_name,
            "severity": severity,
        }
        url = self._construct_url("ws", args, is_websocket=True)
        if self._cli.verify:
            cafile = None
            if isinstance(self._cli.verify, str):
                cafile = self._cli.verify
            ssl_context = ssl.create_default_context(cafile=cafile)
        else:
            ssl_context = ssl.SSLContext()
            ssl_context.verify_mode = ssl.CERT_NONE

        async def nested():
            async with websockets.connect(
                    url, extra_headers=headers, ssl=ssl_context) as ws:
                while True:
                    msg = await ws.recv()
                    as_dict = json.loads(msg)
                    if app_name is None:
                        app = "\033[2m\033[1m%s\x1b[0m" % as_dict["app_name"]
                        spacing = (" " *
                                   (max((22 - len(as_dict["app_name"]), 1))))
                        print("%s>>%s%s" % (app, spacing, as_dict["message"]))
                    else:
                        print(as_dict["message"])

        try:
            asyncio.get_event_loop().run_until_complete(nested())
        except KeyboardInterrupt:
            pass

    def _convert_period_to_timestamp(self, period):
        if period is None:
            return None

        try:
            _ = datetime.datetime.fromtimestamp(int(period))
            return int(period)
        except (OverflowError, OSError):
            LOG.warning("Failed to initialize timestamp from period value: %s",
                        period)
        except ValueError:
            LOG.warning("Invalid value type for period: %s", period)
        units = {
            "s": "seconds",
            "m": "minutes",
            "h": "hours",
            "d": "days",
            "w": "weeks"}
        try:
            count = period[:-1]
            unit = period[-1]
        except Exception:
            raise exceptions.CoriolisException("Failed to parse period")

        conv_unit = units.get(unit)
        if conv_unit is None:
            raise exceptions.CoriolisException("invalid period %s" % period)

        args = {conv_unit: int(count)}
        tm = datetime.datetime.utcnow() - datetime.timedelta(**args)
        return int(tm.timestamp())

    def download_logs(self, app, to, start_time=None, end_time=None):
        if app == "":
            raise exceptions.CoriolisException("missing app_name")

        headers = self._auth_headers
        args = {
            "start_date": self._convert_period_to_timestamp(start_time),
            "end_date": self._convert_period_to_timestamp(end_time),
        }
        resource = "logs/%s/" % app
        url = self._construct_url(resource, args)
        verify = self._cli.verify
        with requests.get(
                url, headers=headers, stream=True, verify=verify) as r:
            r.raise_for_status()
            with open(to, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        fd.write(chunk)

    def list_logs(self):
        headers = self._auth_headers
        url = self._construct_url("logs/")
        req = requests.get(url, headers=headers, verify=self._cli.verify)
        req.raise_for_status()
        ret = req.json()
        return ret.get("logs", [])


class CoriolisLogger(base.Resource):
    pass


class CoriolisLogDownloadManager(base.BaseManager):
    resource_class = CoriolisLogger

    def __init__(self, api):
        super(CoriolisLogDownloadManager, self).__init__(api)
        self._coriolis_cli = LoggingClient(api)

    def list(self):
        logs = self._coriolis_cli.list_logs()
        res = []
        for i in logs:
            res.append(
                self.resource_class(self, i, loaded=True))
        return res

    def get(self, app, to, start_time=None, end_time=None):
        return self._coriolis_cli.download_logs(
            app, to, start_time=start_time, end_time=end_time)

    def stream(self, app_name=None, severity=None):
        self._coriolis_cli.stream_logs(
            app_name=app_name, severity=severity)

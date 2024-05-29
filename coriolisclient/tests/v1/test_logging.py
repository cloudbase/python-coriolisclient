# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import copy
import datetime
import ddt
import requests
import tempfile
from unittest import mock

from keystoneauth1.exceptions import http

from coriolisclient import exceptions
from coriolisclient.tests import test_base
from coriolisclient.v1 import logging


@ddt.ddt
class LoggingClientTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Logging Client."""

    @mock.patch.object(logging.LoggingClient, '_get_endpoint_url')
    def setUp(self, mock_get_endpoint_url):
        mock_get_endpoint_url.return_value = mock.sentinel.ep_url
        mock_client = mock.Mock()
        mock_client.verify = True
        super(LoggingClientTestCase, self).setUp()
        self.logger = logging.LoggingClient(mock_client)
        self.datetime = copy.deepcopy(datetime.datetime)

    @mock.patch.object(logging.LoggingClient, '_get_endpoint_url')
    def test__init__(self, mock_get_endpoint_url):
        mock_get_endpoint_url.side_effect = Exception

        with self.assertLogs(logger=logging.LOG, level="WARNING"):
            logger = logging.LoggingClient(None)

            self.assertEqual(
                None,
                logger._ep_url
            )

    def test_get_endpoint_url(self):
        self.logger._cli.get_endpoint.return_value = "url/endpoint_url/"

        result = self.logger._get_endpoint_url(mock.sentinel.name)

        self.assertEqual(
            "url/endpoint_url",
            result
        )
        self.logger._cli.get_endpoint.assert_called_once_with(
            service_type=mock.sentinel.name)

    def test_get_endpoint_url_not_found(self):
        self.logger._cli.get_endpoint.return_value = None

        self.assertRaises(
            exceptions.LoggingEndpointNotFound,
            self.logger._get_endpoint_url,
            mock.sentinel.name
        )
        self.logger._cli.get_endpoint.assert_called_once_with(
            service_type=mock.sentinel.name)

    def test_get_endpoint_url_http_unauthorized(self):
        self.logger._cli.get_endpoint.side_effect = http.Unauthorized

        with self.assertLogs(logger=logging.LOG, level="ERROR"):
            self.assertRaises(
                exceptions.HTTPAuthError,
                self.logger._get_endpoint_url,
                mock.sentinel.name
            )
            self.logger._cli.get_endpoint.assert_called_once_with(
                service_type=mock.sentinel.name)

    @ddt.data(
        {
            "query_args": {
                "arg1": None,
                "arg2": None
            },
            "is_websocket": True,
            "expected_result":
                "ws:///None/sentinel.resource"
        },
        {
            "query_args": {
                "arg1": None,
                "arg2": "mock_arg2"
            },
            "_ep_url": "https:///ep_url",
            "is_websocket": True,
            "expected_result":
                "wss:///ep_url/sentinel.resource?arg2=mock_arg2"
        },
        {
            "query_args": {
                "arg1": "mock_arg1",
                "arg2": "mock_arg2"
            },
            "_ep_url": "https:///ep_url",
            "is_websocket": False,
            "expected_result": "https:///ep_url/sentinel.resource"
                "?arg1=mock_arg1&arg2=mock_arg2"
        }
    )
    @mock.patch.object(logging.LoggingClient, '_get_endpoint_url')
    def test_construct_url(self, data, mock_get_endpoint_url):
        self.logger._ep_url = None
        mock_get_endpoint_url.return_value = data.get("_ep_url", None)

        result = self.logger._construct_url(
            mock.sentinel.resource,
            data.get("query_args"),
            is_websocket=data.get("is_websocket", False),
        )

        self.assertEqual(
            data.get("expected_result"),
            result
        )

    @ddt.data(
        (None, None, False),
        ("1", 1, False),
        ("1234567890123456789", None, True),
        ("abc", None, True),
        ("", None, True),
    )
    @ddt.unpack
    def test_convert_period_to_timestamp(
        self,
        period,
        expected_result,
        raises
    ):
        if raises is False:
            result = self.logger._convert_period_to_timestamp(period)
            self.assertEqual(
                expected_result,
                result
            )
        else:
            self.assertRaises(
                exceptions.CoriolisException,
                self.logger._convert_period_to_timestamp,
                period
            )

    @mock.patch.object(datetime, 'datetime')
    def test_convert_period_to_timestamp_period(
        self,
        mock_datetime
    ):
        mock_datetime.utcnow.return_value = self.datetime.fromtimestamp(100000)
        result = self.logger._convert_period_to_timestamp("1d")
        self.assertEqual(
            13600,
            result
        )

    @mock.patch.object(requests, "get")
    @mock.patch.object(logging.LoggingClient, "_construct_url")
    @mock.patch.object(logging.LoggingClient, "_convert_period_to_timestamp")
    def test_download_logs(
        self,
        mock_convert_period_to_timestamp,
        mock_construct_url,
        mock_get
    ):
        mock_r = mock.Mock()
        mock_r.iter_content.return_value = [b'test_chunk1', b'test_chunk2']
        mock_get.return_value.__enter__.return_value = mock_r
        with tempfile.NamedTemporaryFile() as fd:
            self.logger.download_logs(
                mock.sentinel.app,
                fd.name,
                start_time=mock.sentinel.start_time,
                end_time=mock.sentinel.end_time
            )

            result = fd.read()
        self.assertEqual(
            result,
            b'test_chunk1test_chunk2'
        )
        mock_get.assert_called_once_with(
            mock_construct_url.return_value,
            headers=self.logger._auth_headers,
            stream=True,
            verify=True
        )
        mock_construct_url.assert_called_once_with(
            "logs/sentinel.app/",
            {
                "start_date": mock_convert_period_to_timestamp.return_value,
                "end_date": mock_convert_period_to_timestamp.return_value,
            }
        )

    def test_download_logs_no_app(self):
        self.assertRaises(
            exceptions.CoriolisException,
            self.logger.download_logs,
            "",
            None
        )

    @mock.patch.object(requests, "get")
    def test_list_logs(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = {
            "logs": ["mock_log1", "mock_log2"]
        }

        result = self.logger.list_logs()

        self.assertEqual(
            ['mock_log1', 'mock_log2'],
            result
        )


class CoriolisLogDownloadManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Coriolis Log Download Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(CoriolisLogDownloadManagerTestCase, self).setUp()
        self.logger = logging.CoriolisLogDownloadManager(mock_client)
        self.logger._coriolis_cli = mock.Mock()
        self.logger.resource_class = mock.Mock()

    def test_list(self):
        self.logger._coriolis_cli.list_logs.return_value = [
            "mock_log1", "mock_log2"]

        result = self.logger.list()

        self.assertEqual(
            [self.logger.resource_class.return_value,
             self.logger.resource_class.return_value],
            result
        )
        self.logger.resource_class.assert_has_calls([
            mock.call(self.logger, "mock_log1", loaded=True),
            mock.call(self.logger, "mock_log2", loaded=True)
        ])

    def test_get(self):
        result = self.logger.get(
            mock.sentinel.app,
            mock.sentinel.to,
            start_time=mock.sentinel.start_time,
            end_time=mock.sentinel.end_time,
        )

        self.assertEqual(
            self.logger._coriolis_cli.download_logs.return_value,
            result
        )
        self.logger._coriolis_cli.download_logs.assert_called_once_with(
            mock.sentinel.app,
            mock.sentinel.to,
            start_time=mock.sentinel.start_time,
            end_time=mock.sentinel.end_time,
        )

    def test_stream(self):
        self.logger.stream(
            app_name=mock.sentinel.app_name,
            severity=mock.sentinel.severity,
        )

        self.logger._coriolis_cli.stream_logs.assert_called_once_with(
            app_name=mock.sentinel.app_name,
            severity=mock.sentinel.severity,
        )

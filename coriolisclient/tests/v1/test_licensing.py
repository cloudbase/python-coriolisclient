# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

import requests

from coriolisclient import exceptions
from coriolisclient.tests import test_base
from coriolisclient.v1 import licensing


class LicensingClientTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Licensing Client."""

    def setUp(self):
        mock_client = mock.Mock()
        super(LicensingClientTestCase, self).setUp()
        self.licence = licensing.LicensingClient(
            mock_client, "endpoint_name")
        mock_client.verify = True
        self.licence._cli = mock_client

    def test_get_licensing_endpoint_url(self):
        self.licence._cli.get_endpoint.return_value = "url/endpoint_url/"

        result = self.licence._get_licensing_endpoint_url()

        self.assertEqual(
            "url/endpoint_url",
            result
        )
        self.licence._cli.get_endpoint.assert_called_once_with(
            service_type="endpoint_name")

    def test_get_licensing_endpoint_url_raises(self):
        self.licence._cli.get_endpoint.side_effect = Exception()

        with self.assertLogs(level="WARN"):
            self.assertRaises(
                exceptions.LicensingEndpointNotFound,
                self.licence._get_licensing_endpoint_url
            )
            self.licence._cli.get_endpoint.assert_called_once_with(
                service_type="endpoint_name")

    @mock.patch.object(licensing.LicensingClient,
                       "_get_licensing_endpoint_url")
    def test_do_req_raw(
        self,
        mock_get_licensing_endpoint_url
    ):
        mock_method = mock.Mock()
        mock_resp = mock.Mock()
        mock_resp.ok = True
        mock_method.return_value = mock_resp
        setattr(requests, "mock_method", mock_method)
        mock_get_licensing_endpoint_url.return_value = 'url/endpoint_url/'
        result = self.licence._do_req(
            method_name="mock_method",
            resource='url/resource_url/',
            body=None,
            response_key=None,
            raw_response=True
        )

        self.assertEqual(
            mock_resp,
            result
        )
        mock_method.assert_called_once_with(
            'url/endpoint_url/url/resource_url/',
            verify=self.licence._cli.verify
        )

    @mock.patch.object(licensing.LicensingClient,
                       "_get_licensing_endpoint_url")
    def test_do_req_json(
        self,
        mock_get_licensing_endpoint_url
    ):
        mock_method = mock.Mock()
        mock_resp = mock.Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"response_key": mock.sentinel.data}
        mock_method.return_value = mock_resp
        setattr(requests, "mock_method", mock_method)
        mock_get_licensing_endpoint_url.return_value = 'url/endpoint_url/'
        result = self.licence._do_req(
            method_name="mock_method",
            resource='url/resource_url/',
            body={"mock_body": "value"},
            response_key='response_key',
            raw_response=False
        )

        self.assertEqual(
            mock.sentinel.data,
            result
        )
        mock_method.assert_called_once_with(
            'url/endpoint_url/url/resource_url/',
            verify=self.licence._cli.verify,
            data='{"mock_body": "value"}'
        )

    @mock.patch.object(licensing.LicensingClient,
                       "_get_licensing_endpoint_url")
    def test_do_req_error(
        self,
        mock_get_licensing_endpoint_url
    ):
        mock_method = mock.Mock()
        mock_resp = mock.Mock()
        mock_resp.ok = False
        mock_resp.json.side_effect = Exception
        mock_resp.raise_for_status.side_effect = exceptions.CoriolisException
        mock_method.return_value = mock_resp
        setattr(requests, "mock_method", mock_method)
        mock_get_licensing_endpoint_url.return_value = 'url/endpoint_url/'

        with self.assertLogs(level="DEBUG"):
            self.assertRaises(
                exceptions.CoriolisException,
                self.licence._do_req,
                method_name="mock_method",
                resource='url/resource_url/',
                body=None,
                response_key='response_key',
                raw_response=False
            )
            mock_method.assert_called_once_with(
                'url/endpoint_url/url/resource_url/',
                verify=self.licence._cli.verify
            )

    @mock.patch.object(licensing.LicensingClient,
                       "_get_licensing_endpoint_url")
    def test_do_req_http_error(
        self,
        mock_get_licensing_endpoint_url
    ):
        mock_method = mock.Mock()
        mock_resp = mock.Mock()
        mock_resp.ok = False
        mock_resp.json.return_value = {"error": {"code": 123, "message": ""}}
        mock_method.return_value = mock_resp
        setattr(requests, "mock_method", mock_method)
        mock_get_licensing_endpoint_url.return_value = 'url/endpoint_url/'

        self.assertRaises(
            exceptions.HTTPError,
            self.licence._do_req,
            method_name="mock_method",
            resource='url/resource_url/',
            body=None,
            response_key='response_key',
            raw_response=False
        )
        mock_method.assert_called_once_with(
            'url/endpoint_url/url/resource_url/',
            verify=self.licence._cli.verify
        )

    @mock.patch.object(licensing.LicensingClient,
                       "_get_licensing_endpoint_url")
    def test_do_req_response_key_error(
        self,
        mock_get_licensing_endpoint_url
    ):
        mock_method = mock.Mock()
        mock_resp = mock.Mock()
        mock_resp.ok = False
        mock_resp.json.return_value = {"response_key": mock.sentinel.data}
        mock_method.return_value = mock_resp
        setattr(requests, "mock_method", mock_method)
        mock_get_licensing_endpoint_url.return_value = 'url/endpoint_url/'

        self.assertRaises(
            ValueError,
            self.licence._do_req,
            method_name="mock_method",
            resource='url/resource_url/',
            body=None,
            response_key='invalid',
            raw_response=False
        )
        mock_method.assert_called_once_with(
            'url/endpoint_url/url/resource_url/',
            verify=self.licence._cli.verify
        )

    def test_do_req_method_error(self):
        setattr(requests, "mock_method", None)

        self.assertRaises(
            ValueError,
            self.licence._do_req,
            method_name="mock_method",
            resource='url/resource_url/',
            body=None,
            response_key='invalid',
            raw_response=False
        )

    @mock.patch.object(licensing.LicensingClient, '_do_req')
    def test_get(self, mock_do_req):
        result = self.licence.get(
            resource=mock.sentinel.resource,
            body=mock.sentinel.body,
            response_key=mock.sentinel.response_key,
            raw_response=False
        )
        self.assertEqual(
            mock_do_req.return_value,
            result
        )
        mock_do_req.assert_called_once_with(
            'GET',
            mock.sentinel.resource,
            response_key=mock.sentinel.response_key,
            body=mock.sentinel.body,
            raw_response=False
        )

    @mock.patch.object(licensing.LicensingClient, '_do_req')
    def test_post(self, mock_do_req):
        result = self.licence.post(
            resource=mock.sentinel.resource,
            body=mock.sentinel.body,
            response_key=mock.sentinel.response_key,
            raw_response=False
        )
        self.assertEqual(
            mock_do_req.return_value,
            result
        )
        mock_do_req.assert_called_once_with(
            'POST',
            mock.sentinel.resource,
            response_key=mock.sentinel.response_key,
            body=mock.sentinel.body,
            raw_response=False
        )

    @mock.patch.object(licensing.LicensingClient, '_do_req')
    def test_delete(self, mock_do_req):
        result = self.licence.delete(
            resource=mock.sentinel.resource,
            body=mock.sentinel.body,
            response_key=mock.sentinel.response_key,
            raw_response=False
        )
        self.assertEqual(
            mock_do_req.return_value,
            result
        )
        mock_do_req.assert_called_once_with(
            'DELETE',
            mock.sentinel.resource,
            response_key=mock.sentinel.response_key,
            body=mock.sentinel.body,
            raw_response=False
        )


class LicensingManagerTestCase(
    test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Licensing Client."""

    @mock.patch.object(licensing, 'LicensingClient')
    def setUp(self, mock_LicensingClient):
        mock_client = mock.Mock()
        super(LicensingManagerTestCase, self).setUp()
        self.licence = licensing.LicensingManager(mock_client)
        self.licence._licensing_cli = mock_LicensingClient

    def test_status(self):
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.status(mock.sentinel.appliance_id)

        self.assertEqual(
            mock_resource_class.return_value,
            result
        )
        self.licence._licensing_cli.get.assert_called_once_with(
            '/appliances/%s/status' % mock.sentinel.appliance_id,
            response_key='appliance_licence_status')
        mock_resource_class.assert_called_once_with(
            self.licence, self.licence._licensing_cli.get.return_value,
            loaded=True)

    def test_list(self):
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class
        self.licence._licensing_cli.get.return_value = {
            "licence1": "mock_licence1",
            "licence2": "mock_licence2"
        }

        result = self.licence.list(mock.sentinel.appliance_id)

        self.assertEqual(
            [mock_resource_class.return_value,
             mock_resource_class.return_value],
            result
        )
        self.licence._licensing_cli.get.assert_called_once_with(
            '/appliances/%s/licences' % mock.sentinel.appliance_id,
            response_key='licences')
        mock_resource_class.assert_has_calls([
            mock.call(self.licence, "licence1", loaded=True),
            mock.call(self.licence, "licence2", loaded=True)
        ])

    def test_register(self):
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.register(
            mock.sentinel.appliance_id, mock.sentinel.licence)

        self.assertEqual(
            mock_resource_class.return_value,
            result
        )
        self.licence._licensing_cli.post.assert_called_once_with(
            '/appliances/%s/licences' % mock.sentinel.appliance_id,
            body=mock.sentinel.licence,
            response_key='licence')
        mock_resource_class.assert_called_once_with(
            self.licence, self.licence._licensing_cli.post.return_value,
            loaded=True)

    def test_show(self):
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.show(
            mock.sentinel.appliance_id, mock.sentinel.licence_id)

        self.assertEqual(
            mock_resource_class.return_value,
            result
        )
        self.licence._licensing_cli.get.assert_called_once_with(
            '/appliances/%s/licences/%s' % (mock.sentinel.appliance_id,
                                            mock.sentinel.licence_id),
            response_key='licence')
        mock_resource_class.assert_called_once_with(
            self.licence, self.licence._licensing_cli.get.return_value,
            loaded=True)

    def test_delete(self):
        mock_resource_class = mock.Mock()
        self.licence.resource_class = mock_resource_class

        result = self.licence.delete(
            mock.sentinel.appliance_id, mock.sentinel.licence_id)

        self.assertEqual(
            self.licence._licensing_cli.delete.return_value,
            result
        )
        self.licence._licensing_cli.delete.assert_called_once_with(
            '/appliances/%s/licences/%s' % (mock.sentinel.appliance_id,
                                            mock.sentinel.licence_id),
            raw_response=True)

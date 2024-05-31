# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import ddt
from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import services


@ddt.ddt
class ServiceManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Service Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(ServiceManagerTestCase, self).setUp()
        self.service = services.ServiceManager(mock_client)

    @mock.patch.object(services.ServiceManager, "_list")
    def test_list(self, mock_list):
        result = self.service.list()

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            "/services", "services")

    @mock.patch.object(services.ServiceManager, "_get")
    def test_get(self, mock_get):
        result = self.service.get(mock.sentinel.service)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            "/services/sentinel.service", "service")

    @mock.patch.object(services.ServiceManager, "_post")
    def test_create(self, mock_post):
        expected_data = {
            "host": mock.sentinel.host,
            "binary": mock.sentinel.binary,
            "topic": mock.sentinel.topic,
            "mapped_regions": mock.sentinel.regions,
            "enabled": True
        }
        expected_data = {"service": expected_data}

        result = self.service.create(
            mock.sentinel.host,
            mock.sentinel.binary,
            mock.sentinel.topic,
            mock.sentinel.regions,
            enabled=True,
        )

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            "/services", expected_data, "service")

    @mock.patch.object(services.ServiceManager, "_put")
    def test_update(self, mock_put):
        result = self.service.update(
            mock.sentinel.service, mock.sentinel.updated_values)

        self.assertEqual(
            mock_put.return_value,
            result
        )
        mock_put.assert_called_once_with(
            "/services/%s" % mock.sentinel.service,
            {"service": mock.sentinel.updated_values}, 'service')

    @mock.patch.object(services.ServiceManager, "_delete")
    def test_delete(self, mock_delete):
        result = self.service.delete(mock.sentinel.service)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            "/services/%s" % mock.sentinel.service)

    @mock.patch.object(services.ServiceManager, "list")
    @ddt.data(
        {
            "host": "mock_host",
            "topic": "mock_topic",
            "expected_service": "service1",
            "raises": False
        },
        {
            "host": "mock_host",
            "topic": "mock_topic_not_found",
            "raises": True
        },
        {
            "host": "mock_host_duplicate",
            "topic": "mock_topic_duplicate",
            "raises": True
        },
        {
            "host": "mock_host_not_found",
            "topic": "mock_topic",
            "raises": True
        },
    )
    def test_find_service_by_host_and_topic(
        self,
        data,
        mock_list
    ):
        self.service1 = mock.Mock()
        self.service2 = mock.Mock()
        self.service3 = mock.Mock()
        self.service1.host = "mock_host"
        self.service1.topic = "mock_topic"
        self.service2.host = "mock_host_duplicate"
        self.service2.topic = "mock_topic_duplicate"
        self.service3.host = "mock_host_duplicate"
        self.service3.topic = "mock_topic_duplicate"
        services = [self.service1, self.service2, self.service3]
        mock_list.return_value = services

        if data.get("raises", False):
            self.assertRaises(
                ValueError,
                self.service.find_service_by_host_and_topic,
                data.get("host"),
                data.get("topic")
            )
        else:
            result = self.service.find_service_by_host_and_topic(
                data.get("host"),
                data.get("topic")
            )
            self.assertEqual(
                getattr(self, str(data.get("expected_service")), None),
                result
            )

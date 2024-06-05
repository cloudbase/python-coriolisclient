# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

"""Defines base class for all tests."""

from keystoneauth1 import exceptions as keystoneauth_exceptions
from oslotest import base as test_base
from oslotest import mock_fixture
from unittest import mock

from coriolisclient import base
from coriolisclient import exceptions
from coriolisclient.tests import testutils

# NOTE(claudiub): this needs to be called before any mock.patch calls are
# being done, and especially before any other test classes load. This fixes
# the mock.patch autospec issue:
# https://github.com/testing-cabal/mock/issues/396
mock_fixture.patch_mock_module()


class CoriolisBaseTestCase(test_base.BaseTestCase):

    def setUp(self):
        super(CoriolisBaseTestCase, self).setUp()


class BaseTestCase(CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Base."""

    def test_getid_uuid(self):
        obj = mock.Mock()

        result = base.getid(obj)

        self.assertEqual(
            obj.uuid,
            result
        )

    def test_getid_id(self):
        obj = mock.Mock()

        result = base.getid(obj, possible_fields=["id"])

        self.assertEqual(
            obj.id,
            result
        )

    def test_getid_id_no_fields(self):
        obj = mock.Mock()

        result = base.getid(obj, possible_fields=None)

        self.assertEqual(
            obj.id,
            result
        )

    def test_getid_none(self):
        obj = "mock_obj"

        result = base.getid(obj, possible_fields=None)

        self.assertEqual(
            obj,
            result
        )

    def test_wrap_unauthorized_exception(self):

        @base.wrap_unauthorized_exception
        def mock_fun(func):
            return func()

        func = mock.Mock()
        result = mock_fun(func)

        self.assertEqual(
            func.return_value,
            result
        )

    def test_wrap_unauthorized_exception_http_unauthorized(self):

        @base.wrap_unauthorized_exception
        def mock_fun(func):
            return func()

        func = mock.Mock()
        func.side_effect = keystoneauth_exceptions.http.Unauthorized()

        with self.assertLogs(logger=base.LOG, level="ERROR"):
            self.assertRaises(
                exceptions.HTTPAuthError,
                mock_fun,
                func
            )


class ResourceTestCase(CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Resource."""

    def setUp(self):
        mock_manager = mock.Mock()
        super(ResourceTestCase, self).setUp()
        self.resource = base.Resource(
            mock_manager,
            {"info": mock.sentinel.info}
        )

    def test__repr__(self):
        result = repr(self.resource)
        self.assertEqual(
            "<Resource info=%s>" % mock.sentinel.info,
            result
        )

    def test_human_id(self):
        self.assertEqual(
            None,
            self.resource.human_id
        )

        class HumanResource(base.Resource):
            HUMAN_ID = True

        mock_manager = mock.Mock()
        resource = HumanResource(
            mock_manager,
            {"name": "mock_name"}
        )

        self.assertEqual(
            "mock_name",
            resource.human_id
        )

    def test_add_details(self):
        new_info = {"new_info": mock.sentinel.new_info}

        self.resource._add_details(new_info)

        self.assertEqual(
            mock.sentinel.new_info,
            self.resource.new_info
        )

    def test_add_details_attribute_already_defined(self):
        info = {"human_id": mock.sentinel.human_id}

        self.resource._add_details(info)

        self.assertEqual(
            None,
            self.resource._info.get("human_id")
        )

    @mock.patch.object(base.Resource, "is_loaded")
    @mock.patch.object(base.Resource, "get")
    def test__getattr__(self, mock_get, mock_is_loaded):
        mock_is_loaded.side_effect = [False, True]
        mock_get.side_effect = lambda: setattr(self.resource, "attr", "value")

        self.assertEqual(
            "value",
            self.resource.attr
        )

    @mock.patch.object(base.Resource, "is_loaded")
    @mock.patch.object(base.Resource, "get")
    def test__getattr__error(self, mock_get, mock_is_loaded):
        mock_is_loaded.side_effect = [False, True]

        self.assertRaises(
            AttributeError,
            self.resource.__getattr__,
            "attr"
        )
        mock_get.assert_called_once()

    @mock.patch.object(base.Resource, "_add_details")
    def test_get(self, mock_add_details):
        self.resource._loaded = False
        self.resource.id = mock.sentinel.id

        self.resource.get()

        mock_add_details.assert_called_once_with(
            self.resource.manager.get.return_value._info)
        self.assertEqual(True, self.resource._loaded)

    @mock.patch.object(base.Resource, "_add_details")
    def test_get_none(self, mock_add_details):
        self.resource._loaded = False
        self.resource.id = mock.sentinel.id
        delattr(self.resource.manager, "get")

        self.resource.get()

        mock_add_details.assert_not_called()

    def test__eq__(self):
        mock_manager = mock.Mock()
        resource2 = base.Resource(
            mock_manager,
            {"info": mock.sentinel.info}
        )

        self.assertEqual(
            (
                True,
                NotImplemented,
            ),
            (
                self.resource.__eq__(resource2),
                self.resource.__eq__("string"),
            )
        )

        resource2._info = {"info": mock.sentinel.info2}

        self.assertEqual(
            False,
            self.resource.__eq__(resource2)
        )

    def test__eq__different_subclasses(self):
        mock_manager = mock.Mock()

        class SubResource1(base.Resource):
            pass

        class SubResource2(base.Resource):
            pass

        resource1 = SubResource1(
            mock_manager,
            {"info": mock.sentinel.info}
        )
        resource2 = SubResource2(
            mock_manager,
            {"info": mock.sentinel.info}
        )

        self.assertEqual(
            False,
            resource1.__eq__(resource2)
        )

    def test_is_loaded(self):
        self.resource._loaded = True
        self.assertEqual(True, self.resource.is_loaded())
        self.resource._loaded = False
        self.assertEqual(False, self.resource.is_loaded())

    def test_set_loaded(self):
        self.resource.set_loaded(True)
        self.assertEqual(True, self.resource._loaded)
        self.resource.set_loaded(False)
        self.assertEqual(False, self.resource._loaded)

    def test_to_dict(self):
        result = self.resource.to_dict()

        self.assertEqual(
            {'info': mock.sentinel.info},
            result
        )


class BaseManagerTestCase(CoriolisBaseTestCase):
    """Test suite for the Coriolis Client Base Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(BaseManagerTestCase, self).setUp()
        self.manager = base.BaseManager(mock_client)

    def test_list(self):
        self.manager.client.get(mock.sentinel.url).json.return_value = {
            "mock_response_key": {
                "data": [mock.sentinel.data1, mock.sentinel.data2]}
        }
        obj_class = mock.Mock()

        result = testutils.get_wrapped_function(self.manager._list)(
            self.manager,
            url=mock.sentinel.url,
            response_key="mock_response_key",
            obj_class=obj_class,
            json=None,
            values_key="data"
        )

        self.assertEqual(
            [obj_class.return_value] * 2,
            result
        )
        obj_class.assert_has_calls([
            mock.call(self.manager, mock.sentinel.data1, loaded=True),
            mock.call(self.manager, mock.sentinel.data2, loaded=True)
        ])

    def test_list_json(self):
        (self.manager.client.post(mock.sentinel.url, json=True).json.
         return_value) = [mock.sentinel.data]
        self.manager.resource_class = mock.Mock()

        result = testutils.get_wrapped_function(self.manager._list)(
            self.manager,
            url=mock.sentinel.url,
            response_key=None,
            obj_class=None,
            json=True,
            values_key=None
        )

        self.assertEqual(
            [self.manager.resource_class.return_value],
            result
        )
        self.manager.resource_class.assert_called_once_with(
            self.manager, mock.sentinel.data, loaded=True)

    def test_get(self):
        self.manager.client.get().json.return_value = {
            "mock_response_key": mock.sentinel.data
        }
        self.manager.resource_class = mock.Mock()

        result = testutils.get_wrapped_function(self.manager._get)(
            self.manager,
            url=mock.sentinel.url,
            response_key="mock_response_key"
        )

        self.assertEqual(
            self.manager.resource_class.return_value,
            result
        )
        self.manager.resource_class.assert_called_once_with(
            self.manager, mock.sentinel.data, loaded=True)

    def test_get_no_response_key(self):
        self.manager.client.get().json.return_value = mock.sentinel.data
        self.manager.resource_class = mock.Mock()

        result = testutils.get_wrapped_function(self.manager._get)(
            self.manager,
            url=mock.sentinel.url,
            response_key=None
        )

        self.assertEqual(
            self.manager.resource_class.return_value,
            result
        )
        self.manager.resource_class.assert_called_once_with(
            self.manager, mock.sentinel.data, loaded=True)

    def test_post(self):
        self.manager.client.post().json.return_value = {
            "mock_response_key": mock.sentinel.data
        }
        self.manager.resource_class = mock.Mock()

        result = testutils.get_wrapped_function(self.manager._post)(
            self.manager,
            url=mock.sentinel.url,
            json=True,
            response_key="mock_response_key",
            return_raw=False
        )

        self.assertEqual(
            self.manager.resource_class.return_value,
            result
        )
        self.manager.resource_class.assert_called_once_with(
            self.manager, mock.sentinel.data)

    def test_post_no_response_key(self):
        self.manager.client.post().json.return_value = mock.sentinel.data
        self.manager.resource_class = mock.Mock()

        result = testutils.get_wrapped_function(self.manager._post)(
            self.manager,
            url=mock.sentinel.url,
            json=False,
            response_key=None,
            return_raw=True
        )

        self.assertEqual(
            mock.sentinel.data,
            result
        )
        self.manager.resource_class.assert_not_called()

    def test_put(self):
        self.manager.client.put().json.return_value = {
            "mock_response_key": mock.sentinel.data
        }
        self.manager.resource_class = mock.Mock()

        result = testutils.get_wrapped_function(self.manager._put)(
            self.manager,
            url=mock.sentinel.url,
            json=True,
            response_key="mock_response_key"
        )

        self.assertEqual(
            self.manager.resource_class.return_value,
            result
        )
        self.manager.resource_class.assert_called_once_with(
            self.manager, mock.sentinel.data)

    def test_put_no_response_key(self):
        self.manager.client.put().json.return_value = mock.sentinel.data
        self.manager.resource_class = mock.Mock()

        result = testutils.get_wrapped_function(self.manager._put)(
            self.manager,
            url=mock.sentinel.url,
            json=False,
            response_key=None
        )

        self.assertEqual(
            self.manager.resource_class.return_value,
            result
        )
        self.manager.resource_class.assert_called_once_with(
            self.manager, mock.sentinel.data)

    def test_patch(self):
        self.manager.client.patch().json.return_value = {
            "mock_response_key": mock.sentinel.data
        }
        self.manager.resource_class = mock.Mock()

        result = testutils.get_wrapped_function(self.manager._patch)(
            self.manager,
            url=mock.sentinel.url,
            json=True,
            response_key="mock_response_key"
        )

        self.assertEqual(
            self.manager.resource_class.return_value,
            result
        )
        self.manager.resource_class.assert_called_once_with(
            self.manager, mock.sentinel.data)

    def test_patch_no_response_key(self):
        self.manager.client.patch().json.return_value = mock.sentinel.data
        self.manager.resource_class = mock.Mock()

        result = testutils.get_wrapped_function(self.manager._patch)(
            self.manager,
            url=mock.sentinel.url,
            json=False,
            response_key=None
        )

        self.assertEqual(
            self.manager.resource_class.return_value,
            result
        )
        self.manager.resource_class.assert_called_once_with(
            self.manager, mock.sentinel.data)

    def test_delete(self):
        result = testutils.get_wrapped_function(self.manager._delete)(
            self.manager,
            url=mock.sentinel.url
        )

        self.assertEqual(
            self.manager.client.delete.return_value,
            result
        )
        self.manager.client.delete.assert_called_once_with(mock.sentinel.url)

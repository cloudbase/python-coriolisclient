# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import ddt
from unittest import mock

from coriolisclient.tests import test_base
from coriolisclient.v1 import regions


@ddt.ddt
class RegionManagerTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis v1 Region Manager."""

    def setUp(self):
        mock_client = mock.Mock()
        super(RegionManagerTestCase, self).setUp()
        self.region = regions.RegionManager(mock_client)

    @mock.patch.object(regions.RegionManager, "_list")
    def test_list(self, mock_list):
        result = self.region.list()

        self.assertEqual(
            mock_list.return_value,
            result
        )
        mock_list.assert_called_once_with(
            "/regions", "regions")

    @mock.patch.object(regions.RegionManager, "_get")
    def test_get(self, mock_get):
        result = self.region.get(mock.sentinel.region)

        self.assertEqual(
            mock_get.return_value,
            result
        )
        mock_get.assert_called_once_with(
            "/regions/sentinel.region", "region")

    @mock.patch.object(regions.RegionManager, "_post")
    def test_create(self, mock_post):
        expected_data = {
            "name": mock.sentinel.name,
            "description": mock.sentinel.description,
            "enabled": False,
        }
        expected_data = {"region": expected_data}

        result = self.region.create(
            mock.sentinel.name,
            description=mock.sentinel.description,
            enabled=False,
        )

        self.assertEqual(
            mock_post.return_value,
            result
        )
        mock_post.assert_called_once_with(
            "/regions", expected_data, "region")

    @mock.patch.object(regions.RegionManager, "_put")
    def test_update(self, mock_put):
        result = self.region.update(
            mock.sentinel.region, mock.sentinel.updated_values)

        self.assertEqual(
            mock_put.return_value,
            result
        )
        mock_put.assert_called_once_with(
            "/regions/%s" % mock.sentinel.region,
            {"region": mock.sentinel.updated_values}, 'region')

    @mock.patch.object(regions.RegionManager, "_delete")
    def test_delete(self, mock_delete):
        result = self.region.delete(mock.sentinel.region)

        self.assertEqual(
            mock_delete.return_value,
            result
        )
        mock_delete.assert_called_once_with(
            "/regions/%s" % mock.sentinel.region)

    @mock.patch.object(regions.RegionManager, "list")
    @ddt.data(
        {
            "region_name_or_id": "mock_name",
            "has_regions_cache": True,
            "expected_region": "region1",
            "raise_on_not_found": True,
            "raises": False
        },
        {
            "region_name_or_id": "mock_name_duplicate",
            "has_regions_cache": True,
            "raise_on_not_found": True,
            "raises": True
        },
        {
            "region_name_or_id": "mock_name4",
            "has_regions_cache": False,
            "expected_region": "region4",
            "raise_on_not_found": True,
            "raises": False
        },
        {
            "region_name_or_id": "mock_name_not_found",
            "has_regions_cache": True,
            "raise_on_not_found": True,
            "raises": True
        },
        {
            "region_name_or_id": "mock_name_not_found",
            "has_regions_cache": True,
            "expected_region": None,
            "raise_on_not_found": False,
            "raises": False
        },
        {
            "region_name_or_id": "mock_id",
            "has_regions_cache": True,
            "expected_region": "region1",
            "raise_on_not_found": True,
            "raises": False
        },
        {
            "region_name_or_id": "mock_id_duplicate",
            "has_regions_cache": True,
            "raise_on_not_found": True,
            "raises": True
        },
        {
            "region_name_or_id": "mock_id4",
            "has_regions_cache": False,
            "expected_region": "region4",
            "raise_on_not_found": True,
            "raises": False
        },
        {
            "region_name_or_id": "mock_id_not_found",
            "has_regions_cache": True,
            "raise_on_not_found": True,
            "raises": True
        },
        {
            "region_name_or_id": "mock_id_not_found",
            "has_regions_cache": True,
            "expected_region": None,
            "raise_on_not_found": False,
            "raises": False
        }
    )
    def test_get_region_by_name_or_id(
        self,
        data,
        mock_list
    ):
        self.region1 = mock.Mock()
        self.region2 = mock.Mock()
        self.region3 = mock.Mock()
        self.region4 = mock.Mock()
        self.region1.id = "mock_id"
        self.region1.name = "mock_name"
        self.region2.id = "mock_id_duplicate"
        self.region2.name = "mock_name_duplicate"
        self.region3.id = "mock_id_duplicate"
        self.region3.name = "mock_name_duplicate"
        self.region4.id = "mock_id4"
        self.region4.name = "mock_name4"
        regions_cache = [self.region1, self.region2, self.region3]
        if data.get("has_regions_cache") is False:
            regions_cache = None
        mock_list.return_value = [self.region4]

        if data.get("raises", False):
            self.assertRaises(
                ValueError,
                self.region.get_region_by_name_or_id,
                data.get("region_name_or_id"),
                regions_cache=regions_cache,
                raise_on_not_found=data.get("raise_on_not_found")
            )
        else:
            result = self.region.get_region_by_name_or_id(
                data.get("region_name_or_id"),
                regions_cache=regions_cache,
                raise_on_not_found=data.get("raise_on_not_found")
            )
            self.assertEqual(
                getattr(self, str(data.get("expected_region")), None),
                result
            )

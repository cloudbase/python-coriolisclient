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


class Region(base.Resource):
    pass


class RegionManager(base.BaseManager):
    resource_class = Region

    def __init__(self, api):
        super(RegionManager, self).__init__(api)

    def list(self):
        return self._list('/regions', 'regions')

    def get(self, region):
        return self._get('/regions/%s' % base.getid(region), 'region')

    def create(self, name, description="", enabled=True):
        data = {
            "name": name,
            "description": description}
        if enabled is not None:
            data['enabled'] = enabled

        return self._post('/regions', {'region': data}, 'region')

    def update(self, region, updated_values):
        data = {
            "region": updated_values
        }
        return self._put(
            '/regions/%s' % base.getid(region), data, 'region')

    def delete(self, region):
        return self._delete('/regions/%s' % base.getid(region))

    def get_region_by_name_or_id(
            self, region_name_or_id, regions_cache=None,
            raise_on_not_found=True):

        if not regions_cache:
            regions_cache = self.list()
        id_matches = [
            region for region in regions_cache
            if region.id == region_name_or_id]
        if id_matches:
            if len(id_matches) > 1:
                raise ValueError(
                    "Multiple matches for region ID '%s': %s" % (
                        region_name_or_id, id_matches))
            return id_matches[0]

        name_matches = [
            region for region in regions_cache
            if region.name == region_name_or_id]
        if name_matches:
            if len(name_matches) > 1:
                raise ValueError(
                    "No matches on ID but multiple matches on name for "
                    "provided region identifier '%s': %s" % (
                        region_name_or_id, name_matches))
            return name_matches[0]

        if raise_on_not_found:
            raise ValueError(
                "Could not find region with name or ID '%s'" % (
                    region_name_or_id))

# Copyright (c) 2018 Cloudbase Solutions Srl
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
"""
Command-line interface sub-commands related to providers.
"""
from cliff import lister
from coriolisclient.cli import formatter


# TODO(aznashwan): find good way to keep this in sync with
# the definitions in Coriolis-core.
# Mapping between provider type IDs and the
# human-readable features they offer:
PROVIDERS_TYPE_FEATURE_MAP = {
    1: "Migration Destination",
    2: "Migration Source",
    4: "Replica Destination",
    8: "Replica Source",
    16: "Endpoints",
    32: "Listing Instances",
    64: "OSMorphing",
    128: "Listing Networks",
    256: "Listing VM Flavors",
    512: "Listing Available Options"
}


class ProvidersFormatter(formatter.EntityFormatter):
    """ Formats dict-like entities with keys 'name' and 'types'.
    Ex: {"name": "openstack", "types": [1, 2, 4, 8, 16, 32, 128, 256]}
    """

    columns = ("Platform",
               "Supported Actions")

    def _get_sorted_list(self, obj_list):
        return sorted(obj_list, key=lambda o: o['name'])

    def _get_formatted_data(self, obj):
        features = ", ".join([
            PROVIDERS_TYPE_FEATURE_MAP[typ] for typ in obj['types']])
        data = (obj['name'],
                features)
        return data


class ListProvider(lister.Lister):
    """ List available providers """

    def get_parser(self, prog_name):
        parser = super(ListProvider, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        pvs = self.app.client_manager.coriolis.providers
        obj_list = pvs.list().providers_list
        return ProvidersFormatter().list_objects(obj_list)

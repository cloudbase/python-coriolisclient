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
import json
import logging

from cliff import lister

from coriolisclient.cli import formatter


LOG = logging.getLogger(__name__)

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
    512: "Listing Available Options",
    524288: "Source Minion Pool Operations",
    1048576: "Destination Minion Pool Operations"
}

PROVIDER_SCHEMA_TYPE_MAP = {
    "connection": 16,
    "destination": 4,
    "source": 8,
    "source_minion_pool": 524288,
    "destination_minion_pool": 1048576
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
        features = []
        for typ in obj['types']:
            if typ in PROVIDERS_TYPE_FEATURE_MAP:
                features.append(PROVIDERS_TYPE_FEATURE_MAP[typ])
            else:
                LOG.debug("Unknown provider type: '%s'", typ)
        data = (obj['name'], ", ".join(features))
        return data


class ProviderSchemasFormatter(formatter.EntityFormatter):
    """ Formats dict-like entities with keys 'type' and 'schema'. """

    columns = ("Schema Type", "Schema")

    def _get_formatted_data(self, obj):
        return (
            obj['type'],
            json.dumps(obj['schema'], indent=4))


class ListProvider(lister.Lister):
    """ List available providers """

    def get_parser(self, prog_name):
        parser = super(ListProvider, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        pvs = self.app.client_manager.coriolis.providers
        obj_list = pvs.list().providers_list
        return ProvidersFormatter().list_objects(obj_list)


class ListProviderSchemas(lister.Lister):
    """ List provider schemas by provider type """

    def get_parser(self, prog_name):
        parser = super(ListProviderSchemas, self).get_parser(prog_name)
        parser.add_argument('platform', help='The platform\'s name')
        parser.add_argument(
            'type',
            help="Provider type. Accepted values: %s" % (
                 list(PROVIDER_SCHEMA_TYPE_MAP.keys())))
        return parser

    def take_action(self, args):
        pvs = self.app.client_manager.coriolis.providers
        if args.type not in PROVIDER_SCHEMA_TYPE_MAP:
            raise ValueError(
                "Unknown provider type '%s'. Supported types are: %s" % (
                    (args.type, list(PROVIDER_SCHEMA_TYPE_MAP.keys()))))
        obj = pvs.schemas_list(
            args.platform,
            PROVIDER_SCHEMA_TYPE_MAP[args.type]).provider_schemas
        return ProviderSchemasFormatter().list_objects(obj)

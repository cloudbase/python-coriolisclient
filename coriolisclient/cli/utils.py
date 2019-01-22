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


import json


def add_storage_mappings_arguments_to_parser(parser):
    """ Given an `argparse.ArgumentParser` instance, add the arguments required
    for the 'storage_mappings' field for both Migrations and Replicas:
        * '--default-storage-backend' will be under 'default_storage_backend'
        * '--disk-storage-mapping's will be under 'disk_storage_mappings'
        * '--storage-backend-mapping's will be under 'storage_backend_mappings'
    """
    parser.add_argument(
        "--default-storage-backend",
        dest='default_storage_backend',
        help="Name of a storage backend on the destination platform to "
             "default to using.")

    # NOTE: arparse will just call whatever 'type=' was supplied on a value
    # so we can pass in a single-arg function to have it modify the value:
    def _split_disk_arg(arg):
        disk_id, dest = arg.split('=')
        return {
            "disk_id": disk_id.strip('\'"'),
            "destination": dest.strip('\'"')}
    parser.add_argument(
        "--disk-storage-mapping", action='append', type=_split_disk_arg,
        dest='disk_storage_mappings',
        help="Mappings between IDs of the source VM's disks and the names of "
             "storage backends on the destination platform as seen by running "
             "`coriolis endpoint storage list $DEST_ENDPOINT_ID`. "
             "Values should be fomatted with '=' (ex: \"id#1=lvm)\"."
             "Can be specified multiple times for multiple disks.")

    def _split_backend_arg(arg):
        src, dest = arg.split('=')
        return {
            "source": src.strip('\'"'),
            "destination": dest.strip('\'"')}
    parser.add_argument(
        "--storage-backend-mapping", action='append', type=_split_backend_arg,
        dest='storage_backend_mappings',
        help="Mappings between names of source and destination storage "
        "backends  as seen by running `coriolis endpoint storage "
        "list $DEST_ENDPOINT_ID`. Values should be fomatted with '=' "
        "(ex: \"id#1=lvm)\". Can be specified multiple times for "
        "multiple backends.")


def get_storage_mappings_dict_from_args(args):
    storage_mappings = {}

    if args.default_storage_backend:
        storage_mappings["default"] = args.default_storage_backend

    if args.disk_storage_mappings:
        storage_mappings["disk_mappings"] = args.disk_storage_mappings

    if args.storage_backend_mappings:
        storage_mappings["backend_mappings"] = args.storage_backend_mappings

    return storage_mappings


def format_mapping(mapping):
    """ Given a str-str mapping, formats it as a string. """
    return ", ".join(
        ["'%s'='%s'" % (k, v) for k, v in mapping.items()])


def parse_storage_mappings(storage_mappings):
    """ Given the 'storage_mappings' API field, returns a tuple with the
    'default' option, the 'backend_mappings' and 'disk_mappings'.
    """
    # NOTE: the 'storage_mappings' property is Nullable:
    if storage_mappings is None:
        return None, {}, {}

    backend_mappings = {
        mapping['source']: mapping['destination']
        for mapping in storage_mappings.get("backend_mappings", [])}
    disk_mappings = {
        mapping['disk_id']: mapping['destination']
        for mapping in storage_mappings.get("disk_mappings", [])}

    return (
        storage_mappings.get("default"), backend_mappings, disk_mappings)


def format_json_for_object_property(obj, prop_name):
    """ Returns the property given by `prop_name` of the given
    API object as a nicely-formatted JSON string (if it exists) """
    prop = getattr(obj, prop_name, None)
    if prop is None:
        # NOTE: return an empty JSON object string to
        # clearly-indicate it's a JSON
        return "{}"

    if not isinstance(prop, dict) and hasattr(prop, 'to_dict'):
        prop = prop.to_dict()

    return json.dumps(prop, indent=2)

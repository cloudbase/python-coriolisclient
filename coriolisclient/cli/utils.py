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


import argparse
import json
import os
import uuid

from coriolisclient import constants


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


def validate_uuid_string(uuid_obj, uuid_version=4):
    """ Checks whether the provided string is a valid UUID string

        :param uuid_obj: A string or stringable object containing the UUID
        :param uuid_version: The UUID version to be used
    """
    uuid_string = str(uuid_obj).lower()
    try:
        uuid.UUID(uuid_string, version=uuid_version)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False

    return True


def add_args_for_json_option_to_parser(parser, option_name):
    """ Given an `argparse.ArgumentParser` instance, dynamically add a group of
    arguments for the option for both an '--option-name' and
    '--option-name-file'.
    """
    option_name = option_name.replace('_', '-')
    option_label_name = option_name.replace('-', ' ')
    arg_group = parser.add_mutually_exclusive_group()
    arg_group.add_argument('--%s' % option_name,
                           help='JSON encoded %s data' % option_label_name)
    arg_group.add_argument('--%s-file' % option_name,
                           type=argparse.FileType('r'),
                           help='Relative/full path to a file containing the '
                                '%s data in JSON format' % option_label_name)
    return parser


def get_option_value_from_args(args, option_name, error_on_no_value=True):
    """ Returns a dict with the value from of the option from the given
    arguments as set up by calling `add_args_for_json_option_to_parser`
    ('--option-name' and '--option-name-file')
    """
    value = None
    raw_value = None
    option_name = option_name.replace('-', '_')
    option_label_name = option_name.replace('_', ' ')
    option_file_name = "%s_file" % option_name
    option_arg_name = "--%s" % option_name.replace('_', '-')

    raw_arg = getattr(args, option_name)
    file_arg = getattr(args, option_file_name)
    if raw_arg:
        raw_value = raw_arg
    elif file_arg:
        with file_arg as fin:
            raw_value = fin.read()

    if not value and raw_value:
        try:
            value = json.loads(raw_value)
        except ValueError as ex:
            raise ValueError(
                "Error while parsing %s JSON: %s" % (
                    option_label_name, str(ex)))

    if not value and error_on_no_value:
        raise ValueError(
            "No '%s[-file]' parameter was provided." % option_arg_name)

    return value


def compose_user_scripts(global_scripts, instance_scripts):
    ret = {
        "global":{},
        "instances": {}
    }
    global_scripts = global_scripts or []
    instance_scripts = instance_scripts or []
    for glb in global_scripts:
        split = glb.split("=", 1)
        if len(split) != 2:
            continue
        if split[0] not in constants.OS_LIST:
            raise ValueError(
                "Invalid OS %s. Available options are: %s" % (
                    split[0], ", ".join(constants.OS_LIST)))
        if os.path.isfile(split[1]) is False:
            raise ValueError("Could not find %s" % split[1])
        with open(split[1]) as sc:
            ret["global"][split[0]] = sc.read()
    
    for inst in instance_scripts:
        split = inst.split("=", 1)
        if len(split) != 2:
            continue
        if os.path.isfile(split[1]) is False:
            raise ValueError("Could not find %s" % split[1])
        with open(split[1]) as sc:
            ret["instances"][split[0]] = sc.read()
    return ret

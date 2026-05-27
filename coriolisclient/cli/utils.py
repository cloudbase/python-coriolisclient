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
from coriolisclient import exceptions


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

    if raw_value:
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


def comma_separated_kv_to_dict(input_string: str) -> dict:
    """Convert a comma separated list of key=value pairs to dict.

    Example: some_key=some_val,some_other_key=some_other_val
             -> {"some_key": "some_val", "some_other_key": "some_other_val"}
    """
    out = {}
    kv_pairs = input_string.split(",")
    for kv_pair in kv_pairs:
        try:
            key, value = kv_pair.split("=")
        except ValueError as err:
            raise ValueError(
                "Not a <key>=<value> pair: %s. " % kv_pair) from err
        out[key] = value
    return out


def compose_user_scripts(
    global_scripts: list[dict],
    instance_scripts: list[dict],
) -> dict:
    """Process user script arguments.

    :param global_scripts: a list of dicts describing user scripts, the target
        OS and the phase in which the scripts should be invoked.
        The dicts are expected to contain the following keys:
            * <os>: one of the operating systems supported by Coriolis,
              e.g. "windows" or "linux". The value will be a local script path.
            * "phase": optional phase, defaults to "osmorphing_post_os_mount".
    :param instance_scripts: a list of dicts describing user scripts, each
        having a corresponding instance.
        The dicts are expected to contain the following keys:
            * <instance>: The name of the instance where the script must run.
            * "phase": optional phase, defaults to "osmorphing_post_os_mount".
    :returns: the processed list of scripts as expected by the Coriolis API.
    """
    ret = {
        "global": {},
        "instances": {}
    }
    global_scripts = global_scripts or []
    instance_scripts = instance_scripts or []
    for params in global_scripts:
        phase = params.pop("phase", constants.PHASE_OSMORPHING_POST_OS_MOUNT)
        if phase not in constants.USER_SCRIPT_PHASES:
            raise ValueError(
                f"Invalid user script phase: {phase}. "
                "Available options are: "
                f"{', '.join(constants.USER_SCRIPT_PHASES)}.")
        if not params:
            raise ValueError(
                "OS type not specified. "
                "Available options are: %s" % ", ".join(constants.OS_LIST))
        if len(params.keys()) > 1:
            raise ValueError(
                "Too many parameters. Expecting just the OS type.")
        os_type = list(params.keys())[0]
        script_path = params[os_type]
        if os_type not in constants.OS_LIST:
            raise ValueError(
                "Invalid OS %s. Available options are: %s" % (
                    os_type, ", ".join(constants.OS_LIST)))

        payload = None
        # The user may omit the script path in order to remove all script
        # records.
        if not script_path:
            ret["global"][os_type] = None
            continue

        if not os.path.isfile(script_path):
            raise ValueError("Could not find %s" % script_path)
        with open(script_path) as sc:
            payload = sc.read()
        if os_type not in ret["global"]:
            ret["global"][os_type] = []
        script_entry = {
            "phase": phase,
            "payload": payload,
        }
        ret["global"][os_type].append(script_entry)

    for params in instance_scripts:
        phase = params.pop("phase", constants.PHASE_OSMORPHING_POST_OS_MOUNT)
        if phase not in constants.USER_SCRIPT_PHASES:
            raise ValueError(
                f"Invalid user script phase: {phase}. "
                "Available options are: "
                f"{', '.join(constants.USER_SCRIPT_PHASES)}.")
        if not params:
            raise ValueError("Instance not specified.")
        if len(params.keys()) > 1:
            raise ValueError(
                "Too many parameters. Expecting just one instance.")
        instance = list(params.keys())[0]
        script_path = params[instance]
        payload = None
        # The user may omit the script path in order to remove all script
        # records.
        if not script_path:
            ret["instances"][instance] = None
            continue

        if not os.path.isfile(script_path):
            raise ValueError("Could not find %s" % script_path)
        with open(script_path) as sc:
            payload = sc.read()
        if instance not in ret["instances"]:
            ret["instances"][instance] = []
        script_entry = {
            "phase": phase,
            "payload": payload,
        }
        ret["instances"][instance].append(script_entry)
    return ret


def add_minion_pool_args_to_parser(
        parser, include_origin_pool_arg=True,
        include_destination_pool_arg=True,
        include_osmorphing_pool_mappings_arg=True):
    if include_origin_pool_arg:
        parser.add_argument(
            '--origin-minion-pool-id',
            help='The ID of a pre-existing Coriolis minion pool associated '
                 'with the origin Coriolis endpoint to use for disk syncing. '
                 'The pool must contain Linux machines.')
    if include_destination_pool_arg:
        parser.add_argument(
            '--destination-minion-pool-id',
            help='The ID of a pre-existing Coriolis minion pool associated '
                 'with the target Coriolis endpoint to use for disk syncing. '
                 'The pool must contain Linux machines.')
    if include_osmorphing_pool_mappings_arg:
        # NOTE: arparse will just call whatever 'type=' was supplied on a value
        # so we can pass in a single-arg function to have it modify the value:
        def _split_pool_mapping_arg(arg):
            instance_id, pool_id = arg.split('=')
            return {
                "instance_id": instance_id.strip('\'"'),
                "pool_id": pool_id.strip('\'"')}

        parser.add_argument(
            '--osmorphing-minion-pool-mapping', action='append',
            dest="instance_osmorphing_minion_pool_mappings",
            type=_split_pool_mapping_arg,
            help='Mapping between the identifier of an instance and a '
                 'pre-existing Coriolis minion pool to be used for its '
                 'OSMorphing. The minion pool must contain machines of the '
                 'same OS type and which are compatible with OSMorphing '
                 'the guest OS of each afferent instance. The mappings must '
                 'be of the form "INSTANCE_IDENTIFIER=MINION_POOL_ID".')


def parse_sort_arg(sort: str | None) -> tuple[list, list]:
    """Parse sort CLI argument.

    :param sort: Comma-separated list of sort keys and directions in the form
                 of <key>[:<asc|desc>]. The direction defaults to descending if
                 not specified.
    :returns: (sort_keys, sort_dirs)
    """
    sort_keys = []
    sort_dirs = []
    if not sort:
        return sort_keys, sort_dirs

    for sort_entry in sort.split(','):
        sort_key, _sep, sort_dir = sort_entry.partition(':')
        if not sort_dir:
            sort_dir = 'desc'
        elif sort_dir not in ('asc', 'desc'):
            raise exceptions.CoriolisException(
                'Unknown sort direction: %s' % sort_dir)
        sort_keys.append(sort_key)
        sort_dirs.append(sort_dir)
    return sort_keys, sort_dirs

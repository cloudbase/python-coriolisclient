"""
Module showcasing various operations on resources exposed
through Coriolis' endpoints API.
"""

import json
import jsonschema

from barbicanclient import client as barbican_client
from keystoneauth1.identity import v3
from keystoneauth1 import session as ksession

from coriolisclient import client as coriolis_client
from coriolisclient import exceptions as coriolis_exceptions


CORIOLIS_CONNECTION_INFO = {
    "auth_url": "http://127.0.0.1:5000/v3",
    "username": "admin",
    "password": "foCVs9hnoSB32dMVNtMLHLaOLDquJUoz1N3p53dd",
    "project_name": "admin",
    "user_domain_name": "default",
    "project_domain_name": "default"
}


# IDs of pre-existing Coriolis endpoints for both platforms.
# Samples relating to endpoint management can be found in 'endpoint_samples.py'
AZURE_ENDPOINT_ID = "67ae217c-d125-498d-82bc-690916900258"
OCI_ENDPOINT_ID = "885fe551-4502-4f55-b24c-1aae96b9ae24"

# Set of options related to the source Azure environment:
AZURE_SOURCE_OPTIONS = {
    "location": "westus",
    "resource_group": "testing-resgroup"
}

# Set of options related to the destination OCI environment:
OCI_DESTINATION_OPTIONS = {
    "availability_domain": "mQqX:EU-FRANKFURT-1-AD-3",
    "compartment": "<OCID of compartment>",
    "vcn_compartment": "<OCID of compartment housing VCNs>",
}

# Mapping between identifiers of networks on the source Azure to VCNs
# in the destination OCI to be used for the NICs of the Migrated VM(s):
NETWORK_MAP = {
    "azure-test-network/azure-test-subnet": "<OCI network OCID>"
}

# Mappings between identifiers of storage elements on the source Azure
# and  available storage typs on the destination OCI to be used for the
# disks of the Migrated VM(s):
STORAGE_MAPPINGS = {
    "default": "standard",
    "backend_mappings": {
        "Premium_LRS": "standard"
    },
    "disk_mappings": {
        "<ID of disk>": "<mapping for specific disk>"
    }
}


def get_schema_for_plugin(coriolis, platform_type, schema_type):
    """ Returns a JSON schema detailing params expected by a given plugin.

    :param platform_type: type of platform (e.g. 'openstack', 'oci', 'azure')
    :param schema_type: schema type(e.g. 'connection', 'source', 'destination')
    :return: dict() containiGng the requrested JSON schema
    """
    provider_schema_type_map = {
        "destination": 1,
        "source": 2,
        "connection": 16
    }

    return coriolis.providers.schemas_list(
        platform_type, provider_schema_type_map[schema_type]).as_dict()


def check_mapped_networks_exist(coriolis, destination_endpoint, network_map,
                                destination_environment=None):
    """ Checks whether all of the mapped networks exist on the destination.

    :param destination_endpoint: destination endpoint object or ID
    :param network_map: network mapping dict
    :param destination_environment: optional environment options for target
    :raises: Exception if a network is not found.
    """
    networks = coriolis.endpoint_networks.list(
        destination_endpoint, environment=destination_environment)

    for mapped_net in network_map.values():
        matches = [
            net for net in networks
            if net.id == mapped_net or net.name == mapped_net]

        if not matches:
            raise Exception(
                "Could not find network '%s' on the destination. Available "
                "networks are: %s" % (mapped_net, networks))


def check_mapped_storage_exists(coriolis, destination_endpoint,
                                storage_mappings,
                                destination_environment=None):
    """ Checks whether all of the mapped storage types exist on the destination.

    :param destination_endpoint: destination endpoint object or ID
    :param storage_mappings: storage mappings dict
    :param destination_environment: optional environment options for target
    :raises: Exception if storage is not found.
    """
    storage = coriolis.endpoint_storage.list(
        destination_endpoint, environment=destination_environment)

    def _check_stor(storage_name_or_id):
        matches = [
            stor for stor in storage
            if stor.id == storage_name_or_id or stor.name == storage_name_or_id]
        if not matches:
            raise Exception(
                "Could not find storage type '%s' in: %s" % (
                    storage_name_or_id, storage))
        return matches[0]

    # check default:
    default = storage_mappings.get('default')
    if default is not None:
        _check_stor(default)

    # check backend mappings:
    for mapped_storage in storage_mappings.get('backend_mappings', {}).values():
        _check_stor(mapped_storage)

    # check per-disk mappings:
    for mapped_storage in storage_mappings.get('disk_mappings', {}).values():
        _check_stor(mapped_storage)


def get_linux_vms_for_endpoint(coriolis, source_endpoint, source_options=None):
    """ Returns a list of the names/IDs of Linux VMs on a source endpoint """
    vms = coriolis.endpoint_instances.list(
        source_endpoint, env=source_options)

    return [vm for vm in vms if vm.os_type == 'linux']


def check_vm_network_mapping(coriolis, source_endpoint, vm_name_or_id, network_map,
                             source_options=None):
    """ Fetches detailed info on the given source VM and checks that all of its
    NICs have an appropriate mapping in the given network_map

    :param source_endpoint: source endpoint name or ID
    :param vm_id: identifier (name or ID) of the the VM on the source
    :param network_map: network mapping
    :param source_options: added source environment options
    """
    vm_info = coriolis.endpoint_instances.get(
        source_endpoint, vm_name_or_id, env=source_options)

    for nic in vm_info['devices']['nics']:
        if nic['network_name'] not in network_map.values():
            raise Exception(
                "Mapped network for NIC with MAC '%s' not found: %s" % (
                    nic['mac_address'], nic['network_name']))


def main():
    session = ksession.Session(
        auth=v3.Password(**CORIOLIS_CONNECTION_INFO))

    coriolis = coriolis_client.Client(session=session)
    barbican = barbican_client.Client(session=session)

    # fetch and validate options for Azure:
    oci_schema = get_schema_for_plugin(
        'coriolis', 'oci', 'destination')
    # NOTE: this parameter validation is also done in ay API
    # call involving the OCI destination options:
    jsonschema.validate(OCI_DESTINATION_OPTIONS, oci_schema)

    # fetch and validate options schema for OCI:
    oci_schema = get_schema_for_plugin(
        'coriolis', 'oci', 'destination')
    # NOTE: this parameter validation is also done in ay API
    # call involving the OCI destination options:
    jsonschema.validate(OCI_DESTINATION_OPTIONS, oci_schema)

    # list all available options on source or target:
    azure_options = coriolis.endpoint_source_options.list(
        AZURE_ENDPOINT_ID, environment=AZURE_SOURCE_OPTIONS)
    print("Avaialble Azure options are: ", json.dumps(azure_options, indent=4))
    oci_options = coriolis.endpoint_destination_options.list(
        OCI_ENDPOINT_ID, environment=OCI_DESTINATION_OPTIONS)
    print("Avaialble OCI options are: ", json.dumps(oci_options, indent=4))

    # check all mapped networks and storage exist:
    check_mapped_networks_exist(
        coriolis, OCI_ENDPOINT_ID, NETWORK_MAP,
        destination_environment=OCI_DESTINATION_OPTIONS)
    check_mapped_storage_exists(
        coriolis, OCI_ENDPOINT_ID, NETWORK_MAP,
        destination_environment=OCI_DESTINATION_OPTIONS)

    # get list of Linux VMs off of Azure:
    azure_linux_vms = get_linux_vms_for_endpoint(
        coriolis, AZURE_ENDPOINT_ID, source_options=AZURE_SOURCE_OPTIONS)
    print("Linux VMs currently on Azure: %s" % azure_linux_vms)

    # check network mapping:
    if azure_linux_vms:
        vm_name = azure_linux_vms[0].instance_name
        check_vm_network_mapping(
            coriolis, AZURE_ENDPOINT_ID, vm_name, NETWORK_MAP,
            source_options=AZURE_SOURCE_OPTIONS)

""" Module showcasing various operations relating to Coriolis Replicas. """

import json
import time

from keystoneauth1.identity import v3
from keystoneauth1 import session as ksession

from coriolisclient import client as coriolis_client


CORIOLIS_CONNECTION_INFO = {
    "auth_url": "http://127.0.0.1:5000/v3",
    "username": "admin",
    "password": "foCVs9hnoSB32dMVNtMLHLaOLDquJUoz1N3p53dd",
    "project_name": "admin",
    "user_domain_name": "default",
    "project_domain_name": "default"
}


# Name of pre-existing source VM used in these examples:
SOURCE_VM_NAME = "coriolis-test-vm"

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
    "migr_shape_name": "VM.Standard2.1",
    "migr_subnet_id": "<destination-subnet-OCID>",
    "compartment": "<compartment OCID>",
    "set_public_ip": True,
    "migr_image_map": {"linux": "<linux image OCID>"},
    "vcn_compartment": "<compartment OCID housing VCNS>",
}

# Mapping between identifiers of networks on the source Azure to VCNs
# in the destination OCI to be used for the NICs of the Migrated VM(s):
NETWORK_MAP = {
    "source-network/source-subnet": {
        "id": "<destination network OCID>",
        "security_groups": ["<destination secgroup OCID>"]
    }
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


def create_vm_replicas(coriolis, source_endpoint, destination_endpoint,
                       source_options, destination_options, network_map,
                       storage_mappings, vms, separate_replica_per_vm=False):
    """ Creates Replica(s) for the given VMs with the provided parameters.

    :param source/destination_endpoint: endpoint names or IDs
    :param source/destination_options: extra options relating to source/target
    :param network_map: mapping between source and target networks
    :param storage_mappings: mappings for storage
    :param vms: list of source VM names/indentifiers
    :param separate_replica_per_vm: whether or not to create separate Replica
    for each VM. This is useful for more granular transfers.
    """
    replicas = []
    vm_groupings = [vms]
    if separate_replica_per_vm:
        vm_groupings = [[vm] for vm in vms]

    existing_source_vms = [
        (vm.id, vm.instance_name)
        for vm in coriolis.endpoint_instances.list(
            source_endpoint, env=source_options)]

    for vm_group in vm_groupings:
        for vm_name_or_id in vm_group:
            matches = [
                ex for ex in existing_source_vms
                if vm_name_or_id in ex]
            if not matches:
                raise Exception(
                    "Could not find source VM '%s' on source endpoint '%s'" % (
                        vm_name_or_id, source_endpoint))

        print("Creating Replica for VM(s): %s" % vm_group)
        replicas.append(
            coriolis.transfers.create(
                source_endpoint, destination_endpoint,
                source_options, destination_options,
                vm_group,
                network_map=network_map,
                storage_mappings=storage_mappings))

    return replicas


def get_replicas_for_endpoint(coriolis, endpoint,
                              as_source=True, as_target=True):
    """ Returns all Replicas with the given endpoint as source/target. """
    endpoint = coriolis.endpoints.get(endpoint)

    found = []
    for replica in coriolis.transfers.list():
        if as_source and replica.origin_endpoint_id == endpoint.id:
            found.append(replica)

        if as_target and replica.destination_endpoint_id == endpoint.id:
            found.append(replica)

    return found


def get_replicas_for_vm(coriolis, vm_name):
    """ Returns all Replicas which include the given VM name. """
    replicas = []
    for replica in coriolis.transfers.list():
        if vm_name in replica.instances:
            replicas.append(replica)

    return replicas


def get_errord_replicas(coriolis):
    """ Returns a list of all the Replicas whose last execution error'd. """
    errord = []
    for replica in coriolis.transfers.list():
        if not replica.executions:
            # Replica was never executed
            continue

        if replica.executions[-1].status == 'ERROR':
            errord.append(replica)

    return errord


def wait_for_replica_execution(coriolis, replica, execution,
                               max_tries=600, retry_period=5):
    """ Waits for a maximum amount of time for a given execution to finish.

    :param execution: Replica Execution object
    :param max_tries: maximum number of state queries before giving up
    :param retry_period: time to wait between retries
    """
    tries = 0

    execution = coriolis.transfer_executions.get(
        replica, execution)
    while tries < max_tries and execution.status == "RUNNING":
        print("Waiting on execution %s (currently %s)" % (
            execution.id, execution.status))
        time.sleep(retry_period)
        execution = coriolis.transfer_executions.get(
            replica, execution)

        if execution.status == "ERROR":
            break
        tries = tries + 1

    if execution.status != "COMPLETED":
        raise Exception(
            "Replica Execution '%s' reached improper status: %s" % (
                execution.id, execution.status))

    return execution


def wait_for_replica_migration(coriolis, migration, max_tries=600,
                               retry_period=5):
    """ Waits for a maximum amount of time for a given Migration to finish.

    :param migration_id: Migration object/ID
    :param max_tries: maximum number of state queries before giving up
    :param retry_period: time to wait between retries
    """
    tries = 0

    migration = coriolis.migrations.get(migration)
    while tries < max_tries and migration.status == "RUNNING":
        print("Waiting on migration %s (currently %s)" % (
            migration.id, migration.status))
        time.sleep(retry_period)
        migration = coriolis.migrations.get(migration)

        if migration.status == "ERROR":
            break
        tries = tries + 1

    if migration.status != "COMPLETED":
        raise Exception(
            "Migration '%s' reached improper status: %s" % (
                migration.id, migration.status))

    return migration


def delete_replica(coriolis, replica, delete_replica_disks=True):
    """ Deletes the given Replica from Coriolis.

    :param delete_replica_disks: whether or not to delete the Replica backup
                                 disks from the target platform before deleting
                                 the Replica itself.
    """
    if delete_replica_disks:
        execution = coriolis.transfers.delete_disks(replica)
        wait_for_replica_execution(coriolis, replica, execution)

    # NOTE: this is redundant as executions are cascade-deleted on
    # the deletion of the parent Replica anyway:
    for execution in reversed(replica.executions):
        coriolis.transfer_executions.delete(execution)

    coriolis.transfers.delete(replica)


def main():
    session = ksession.Session(
        auth=v3.Password(**CORIOLIS_CONNECTION_INFO))

    coriolis = coriolis_client.Client(session=session)

    # see how may Replicas from Azure we already have:
    azure_replicas = get_replicas_for_endpoint(
        coriolis, AZURE_ENDPOINT_ID, as_source=True, as_target=False)
    print(
        "Existing Azure Replicas for endpoint '%s': %s" % (
            AZURE_ENDPOINT_ID, azure_replicas))

    # create a Replica:
    replicas = create_vm_replicas(
        coriolis, AZURE_ENDPOINT_ID, OCI_ENDPOINT_ID,
        AZURE_SOURCE_OPTIONS, OCI_DESTINATION_OPTIONS,
        NETWORK_MAP, STORAGE_MAPPINGS, [SOURCE_VM_NAME])

    # execute the Replica:
    test_replica = replicas[0]
    execution = coriolis.transfer_executions.create(
        test_replica, shutdown_instances=True)

    # wait for execution to finish:
    wait_for_replica_execution(coriolis, test_replica, execution)

    # create a Migration from the Replica:
    migration = coriolis.migrations.create_from_transfer(
        test_replica.id, clone_disks=True, skip_os_morphing=False)
    migration = wait_for_replica_migration(coriolis, migration)
    print("Migrated VM info is: %s" % (
        json.dumps(migration.transfer_result.to_dict(), indent=4)))

    # delete the Migration (this has *NO* effect on the migrated VM(s))
    coriolis.migrations.delete(migration)

    # delete the Replica once done:
    delete_replica(coriolis, test_replica, delete_replica_disks=True)

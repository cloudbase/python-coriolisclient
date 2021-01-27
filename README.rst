Python bindings to the Coriolis migration API
=============================================

* License: Apache License, Version 2.0
* `PyPi`_ - package installation

.. _PyPi: https://pypi.python.org/pypi/python-coriolisclient

Command-line API
----------------

The Coriolis Command-line API offers an interface over the REST API provided by
the Coriolis migration service.

Coriolis uses Keystone for identity management. Credentials and endpoints can
be provided via environment variables or command line parameters in the same
way supported by most OpenStack command line interface (CLI) tools, e.g.::

    export OS_AUTH_URL=http://example.com:5000/v2.0
    export OS_USERNAME=admin
    export OS_PASSWORD=blahblah
    export OS_TENANT_NAME=admin

Secrets
-------

In order to migrate virtual workloads, Coriolis requires access to external
environments, e.g. VMware vSphere, AWS, Azure, etc.

Connection details including credentials can be stored in Barbican,
OpenStack's project for secure storage and secrets management::

    VMWARE_CONN_INFO='{"host": "example.com", "port": 443, "username":
    "user@example.com", "password": "blahblah", "allow_untrusted": true}'

    barbican secret store --payload "$VMWARE_CONN_INFO" \
    --payload-content-type "text/plain"

The returned ``Secret href`` is the id of the secret to be referenced in order
to access its content.


Providers
---------

A ``provider`` is a registered extension that supports a given cloud or
virtual environment, like OpenStack, Azure, AWS, VMware vSphere, etc.

There are two types of providers: origin and destination. For example, when
migrating a VM from VMware vSphere to OpenStack, ``wmware_vsphere`` is the
origin and ``openstack`` the destination.

Listing providers::

    coriolis provider list

Listing provider schema::

    coriolis provider schema list $PLATFORM $PROVIDER_TYPE


Endpoints
---------

Coriolis Endpoints are composed of the set of credentials and other
connection-related options specific to a certain cloud account. They are
used to uniquely identify clouds within Coriolis and referenced when
launching migrations/replicas. By default, a plaintext, cloud-specific
set of JSON credentials may be used to create a new Coriolis endpoint,
though passing a reference to a secret stored in Barbican is also possible,
should Barbican be deployed alongside or later hooked up to the Coriolis
deployment.

Creating an endpoint::

    coriolis endpoint create \
    --name $ENDPOINT_NAME \
    --provider $ENDPOINT_PROVIDER \
    --description $DESCRIPTION \
    --connection{-file,} $JSON_ENCODED_CONNECTION_{FILE,STRING}
    (or --connection-secret $BARBICAN_SECRET_URL in case Barbican secrets are used)

Listing the existing endpoints::

    coriolis endpoint list

Showing all deteails of an endpoint::

    coriolis endpoint show $ENDPOINT_ID

Listing the instances on an endpoint::

    coriolis endpoint instance list $ENDPOINT_ID


Coriolis Worker Service Management
-----------------------

The Coriolis Worker Services (which are the Coriolis components which
actually interact with the source/destination platforms to perform the
various operations required for the requested VM transfers) can be
scaled out horizontally across multiple environments to improve load
balance and reliability. (especially during DRaaS operations)


The Worker Services will register themselves on startup, and are primarily
identified by their hostnames (which must be unique)::

    coriolis service list
    coriolis service show $SERVICE_ID


Worker Services can be enabled/disabled by the Coriolis Administrator as
needed by running the following::

    coriolis service update --enabled/--disabled $SERVICE_ID

A disabled Worker Service will no longer have tasks allocated to it by the
Coriolis scheduler, and thus can be brought down for updates/maintenance.


Coriolis Regions
----------------

There are cases where only certain Worker Services can operate on certain
platforms, such as:

- DRaaS operations with multiple Worker Services deployed on both platforms
- performing a transfer from a public cloud platform to a private one
  where the data path is unidirectional

Coriolis offers the ability to group both the source/destination platforms,
and the Worker Services which should be able to access them into so-called
'Coriolis Regions'.
Coriolis Regions are solely meant for categorisation purposes, and can be
defined freely at the Coriolis Administrator's leisure.

Example of region-related oprations include::

    coriolis region create \
        --enabled/disabled \
        --description "This a Coriolis region for public clouds"
        Public
    coriolis region show $REGION_ID
    coriolis region update \
        --enabled/disabled \
        --description "This is the Region's new description." \
        --name "This is the Region's new name." \
        $REGION_ID


Regions can then be associated with Coriolis Endpoints and Coriolis Services
as seen fit for the Coriolis deployment at hand using the following::

    coriolis endpoint update \
        --coriolis-region $REGION_1_ID \
        --coriolis-region $REGION_2_ID \
        $ENDPOINT_ID
    coriolis service update \
        --coriolis-region $REGION_2_ID \
        --coriolis-region $REGION_3_ID \
        $WORKER_SERVICE_ID


The above will associate the given Coriolis Endpoint with two regions, and the
given Coriolis Worker Service with one of the two Regions.

In the above setup, the following properties will hold true:

- any operation performed on the Coriolis Endpoint in question (e.g. listing
  environment options, Migrating or Performing DRaaS to/from that endpoint)
  will be scheduled on a Coriolis Worker Service which is associated to one
  of the Regions the endpoint is associated with
- the Coriolis Worker Service in question will be used for operations relating
  to any Endpoint which is associated to the Coriolis Region '$REGION_2_ID'
  or '$REGION_3_ID'
- if a Coriolis Endpoint has no regions associated to it whatsoever, then any
  operations perfoemd on the Endpoint can be scheduled on any Coriolis Worker
  Service, regardless of the Worker Service's Region associations


Minion Machine Pools
--------------------

Coriolis relies on temporary machines it deploys on the source/target platforms
to perform various actions during transfer operations, such as export/import
the disk data of VMs being migrated, or performing the OSMorphing process.
(where a temporary VM modifes a transferred machine's VM image to ensure it
will boot properly on the target platform)

By default, Coriolis automatically creates and cleans up all of the temporary
reources it needs throughout the duration of the transfer, thus only limiting
resources usage to the duration of the transfer itself, but at the cost of some
time overhead for the actual creation/cleanup of the temporary resources.

In cases where resource usage limitations are not a factor, or where the time
cost outweighs the resource allocation costs, Coriolis offers the ability to
pre-allocate temporary resources on source/destination platforms into so-called
'minion pools'.

For most plugins, the set of parameters related to Minion Pool Machines are
usually shared with the Destination Environment parameters so as to allow
for the dynamic selection of whether or not to use a minion pool or perform
creation/cleanup of temporary resources as usual.

Minion pools can be created through the following::

    coriolis minion pool create \
        --pool-endpoint $ENDPOINT_ID \
        --pool-platform source \
        --pool-os-type linux \
        # Options can be obtained by running the following command:
        # coriolis endpoint minion pool source/destination options list $EID
        --environment-options '{"plugin-specific": "env options"}' \
        --minimum-minions 3 \
        --notes "Some options notes on the pool." \
        $POOL_NAME

The available parameters for minion pools include:

- ``--pool-endpoint``: the ID of the Coriolis Endpoint for the pool.
  The Endpoint must be for a platform whose Provider Plugin supports Minon Pool
  management.
- ``--pool-platform``: whether or not this should be used as a source or
  destination Minion Pool.
  The distinction is in place due to source pools requirings pecial
  setup steps to allow them to export VM data, while destination pools are
  specially deployed to import VM data to the destination paltform and/or
  perform OSMorphing.
- ``--pool-os-type``: the OS type ('linux', 'windows', or otherwise) for the
  Minion Pool. Source Minion Pools require them to be of OS type Linux in order
  to be able to run the data exports during VM transfers.
- ``--environment-options``: JSON data with platform-specific environment
  options for the Minion Pool. These will usually allow for the selection of
  properties such as the image to be used for the temporary machines. Care
  should be taken to pick properties which match the declared ``--pool-os-type``
- ``--minimum-minions``: strictly positive number of Minion Machines the pool
  should contain once allocated.

Additional operations on minion pools include::

    # inspect existing pools:
    coriolis minion pool list
    coriolis minion pool show $POOL_ID

    # allocate Minion Pool resources:
    coriolis minion pool allocate $POOL_ID

    # use a Minion Pool for a Replica or Migration
    coriolis replica/migration create \
        # NOTE: additional required parameters listed in their
        # respective sections further below.
        --instance $INSTANCE1 --instance $INSTANCE2 \
        --origin-minion-pool-id $SOURCE_POOL_ID \
        --destination-minion-pool-id $TARGET_POOL_1_ID \
        --osmorphing-minion-pool-mapping $INSTANCE1=$TARGET_POOL_2_ID

    # deallocate Minion Pool resources:
    coriolis minion pool deallocate $POOL_ID

    # tear down pool shared resources:
    coriolis minion pool tear down shared resources $POOL_ID

    # update a Minion Pool (can be done only if the pool has had its
    # machines deallocated and its shared resources torn down)
    coriolis minion pool update \
        # NOTE: all the paramters for 'minion pool create' can be modified except
        # for the selected minion pool `--pool-endpoint` and `--pool-platform`.
        --arguments-to-update ... \
        $POOL_ID

    # delete a minion pool (only if all of its machines/resources were torn down)
    coriolis minion pool delete $POOL_ID

Once created, Minion Pools can then be used when creating Migrations or Replica
jobs using the ``--origin-minion-pool-id``, ``--destination-minion-pool-id``,
and ``--osmorphing-minion-pool-mapping`` arguments as shown in their respective
sections.

Destination environment
-----------------------

A destination environment defines a set of provider specific parameters that
override both the global configuration and built-in defaults of the Coriolis
worker process(es). For example in the case of the OpenStack's provider, the
following JSON formatted values allow for the definition of a custom mapping
between origin and Neutron networks, another mapping for source storage
backends to Cinder volume types, along with a specific Nova flavor for the
migrated instance and a custom worker image name::

    DESTINATION_ENV='{"network_map": {"VM Network Local": "public", "VM Network":
    "private"}, "storage_map": {"san2": "ssd"}, "flavor_name": "m1.small",
    "migr_image_name": "Nano"}'


Source environment
------------------

A source environment is an optional parameter that defines
provider-specific source parameters

Network map
-----------

The network map is a JSON mapping between identifiers of networks on the source
platform, each being associated with the identifier of a network on the
destination. The values to be mapped depend on the source and destination
provider plugins, respectively (ex: it may be the name of a network, or the
full ID)::



    NETWORK_MAP={"VM Network Local": "public", "VM Network": "internal"}

Default storage backend
-----------------------

Name of a storage backend on the destination platform to default to using::

    DEFAULT_STORAGE_BACKEND="iscsi"


Disk storage mapping
--------------------
The names of storage backends on the destination platform
as seen by running `coriolis endpoint storage list
$DEST_ENDPOINT_ID`. Values should be fomatted with '='
(ex: "id#1=lvm)". Can be specified multiple times for
multiple disks::

    DISK_STORAGE_MAPPINGS="afsan1=lvm"

Storage backend mapping
-----------------------
Mappings between names of source and destination
storage backends as seen by running `coriolis endpoint
storage list $DEST_ENDPOINT_ID`. Values should be
fomatted with '=' (ex: "id#1=lvm)". Can be specified
multiple times for multiple backends::

    STORAGE_BACKEND_MAPPINGS="afsan1=lvm"


Starting a migration
--------------------

Various types of virtual workloads can be migrated, including instances,
templates, network configurations and storage.

The following command migrates a virtual machine between two clouds denoted
by their Coriolis endpoint IDs::

    coriolis migration create \
    --origin-endpoint $ENDPOINT_1_ID \
    --origin-minion-pool-id $OPTIONAL_SOURCE_MINION_POOL_ID \
    --destination-endpoint $ENDPOINT_2_ID \
    --destination-minion-pool-id $OPTIONAL_DESTINATION_MINION_POOL_ID \
    --source-environment{-file,} "$SOURCE_ENVIRONMENT_{FILE,STRING}" \
    --destination-environment{-file,} "$DESTINATION_ENV_{FILE,STRING}" \
    --network-map{-file,} "$NETWORK_MAP_{FILE,STRING}" \
    --default-storage-backend $DEFAULT_BACKEND \
    --disk-storage-mapping $DISK_STORAGE_MAPPING \
    --storage-backend-mapping $STORAGE_BACKEND_MAPPINGS \
    --osmorphing-minion-pool-mapping $VM_NAME=$OPTIONS_DESTINATION_MINION_POOL \
    --instance $VM_NAME

List all migrations
-------------------

The following command retrieves a list of all migrations, including their
status::

    coriolis migration list

Show migration details
----------------------

Migrations can be fairly long running tasks. This command is very useful to
retrieve the current status and all progress updates::

    coriolis migration show $MIGRATION_ID

Cancel a migration
------------------

A pending or running migration can be canceled anytime::

    coriolis migration cancel $MIGRATION_ID

Delete a migation
-----------------

Only migrations in pending or error state can be deleted. Running migrations
need to be first cancelled::

    coriolis migration delete $MIGRATION_ID

Creating a replica
------------------

The process of creating replicas is similar to starting migrations::

    coriolis replica create \
    --origin-endpoint $ENDPOINT_1_ID \
    --origin-minion-pool-id $OPTIONAL_SOURCE_MINION_POOL_ID \
    --destination-endpoint $ENDPOINT_2_ID \
    --destination-minion-pool-id $OPTIONAL_DESTINATION_MINION_POOL_ID \
    --source-environment{-file,} "$SOURCE_ENVIRONMENT_{FILE,STRING}" \
    --destination-environment{-file,} "$DESTINATION_ENV_{FILE,STRING}" \
    --network-map{-file,} "$NETWORK_MAP_{FILE,STRING}" \
    --default-storage-backend $DEFAULT_BACKEND \
    --disk-storage-mapping $DISK_STORAGE_MAPPING \
    --storage-backend-mapping $STORAGE_BACKEND_MAPPINGS \
    --osmorphing-minion-pool-mapping $VM_NAME=$OPTIONS_DESTINATION_MINION_POOL \
    --instance $VM_NAME

Updating a replica
------------------

To update a replica::

    coriolis replica update  $REPLICA_ID \
    --origin-minion-pool-id $OPTIONAL_SOURCE_MINION_POOL_ID \
    --destination-minion-pool-id $OPTIONAL_DESTINATION_MINION_POOL_ID \
    --source-environment{-file,} "$SOURCE_ENVIRONMENT_{FILE,STRING}" \
    --destination-environment{-file,} "$DESTINATION_ENV_{FILE,STRING}" \
    --network-map{-file,} "$NETWORK_MAP_{FILE,STRING}" \
    --default-storage-backend $DEFAULT_BACKEND \
    --disk-storage-mapping $DISK_STORAGE_MAPPING \
    --storage-backend-mapping $STORAGE_BACKEND_MAPPINGS \
    --osmorphing-minion-pool-mapping $VM_NAME=$OPTIONS_DESTINATION_MINION_POOL

Executing a replica
-------------------

After defining a replica in Coriolis, you have to actually launch so-called
replica executions in order for the replication process to kick off.
With each replica execution, the VM's storage elements on the source
environment are 'replicated' directly into storage elements on the
destination, practically creating cross-cloud backups of your instances
which are continuously updated. A replica execution would imply transferring
only the necessary changes to synchronize the state of the storage elements
of the destination, thus the first execution of a replica will always mean
a full transfer of the source storage elements (albeit only of the allocated
blocks), with all subsequent executions implying only transfer of the changed
blocks. Replica executions may then be booted into fully-fledged instances
on the destination cloud should failover from the source environment be
required.

To execute a replica::

    coriolis replica execute $REPLICA_ID

To list all the executions of a replica::

    coriolis replica execution list $REPLICA_ID

To cancel a specific execution of a replica::

    coriolis replica execution cancel $REPLICA_ID $EXECUTION_ID

To delete a specific execution of a replica::

    coriolis replica execution delete $REPLICA_ID $EXECUTION_ID

Showing a replica
-----------------

To retrieve the current status of a replica ::

    coriolis replica show $REPLICA_ID

And to do that for a particular execution of a replica::

    coriolis replica execution show $REPLICA_ID $EXECUTION_ID

Deploying a replica
-------------------

Replicas can be deployed into full VMs with::

    coriolis migration deploy replica \
        --destination-minion-pool-id $OPTIONAL_DESTINATION_MINION_POOL_ID \
        --origin-minion-pool-id $OPTIONAL_SOURCE_MINION_POOL_ID \
        # NOTE: these fully override the OSMorphing pool selections on the Replica:
        --osmorphing-minion-pool-mapping $VM_NAME=$OPTIONS_DESTINATION_MINION_POOL \
        $REPLICA_ID

As this process may take some time, it is useful to know that it can be
interacted with just like a regular migration (i.e. coriolis migration
show $ID).

Listing all replicas
--------------------

To list the currently existing replicas::

    coriolis replica list

Deleting a replica
------------------

To delete a replica::

    coriolis replica delete $REPLICA_ID

Deleting replica target disks
-----------------------------

To delete a replica's target disks::

    coriolis replica disks delete $REPLICA_ID

Creating replica execution schedule
-----------------------------------

To create a schedule for the execution of a replica, with UTC time::

    coriolis replica schedule create \
    $REPLICA_ID \
    -M $MINUTE -H $HOUR -d $DAY -m $MONTH

Listing all replica execution schedules
---------------------------------------

To list the currently existing schedules of a replica::

    coriolis replica schedule list $REPLICA_ID

Showing a replica execution schedule
------------------------------------

To retrieve the current status of a replica execution schedule::

    coriolis replica schedule show  $REPLICA_ID $SCHEDULE_ID

Deleting a replica execution schedule
-------------------------------------

To delete a replica execution schedule::

    coriolis replica schedule delete  $REPLICA_ID $SCHEDULE_ID

Updating a replica execution schedule
-------------------------------------

To update a replica execution schedule::

    coriolis replica schedule update  $REPLICA_ID $SCHEDULE_ID \
    -M $MINUTE -H $HOUR -w $WEEK_DAY \


Python API
----------

The Python interface matches the underlying REST API, it's used by the CLI and
can be employed in 3rd party projects::

    >>> from coriolisclient import client
    >>> c = client.Client(session=keystone_session)
    >>> c.migrations.list()
    [...]
    >>> c.migrations.get(migration_id)
    [...]

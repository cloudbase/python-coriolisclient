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

Target environment
------------------

A target environment defines a set of provider specific parameters that can
override default options set by the Coriolis work processes. For example in the
case of the OpenStack's provider, the following JSON formatted values allow to
specify a custom mapping between origin and Neutron networks, along with a
specific Nova flavor for the migrated instance and a custom worker image name::

    TARGET_ENV='{"network_map": {"VM Network Local": "public", "VM Network":
    "private"}, "flavor_name": "m1.small", "migr_image_name": "Nano"}'


Starting a migration
--------------------

Various types of virtual workloads can be migrated, including instances,
templates, network configurations and storage.

The following command migrates a virtual machine named ``VM1`` from VMware
vSphere to OpenStack::

    coriolis migration create --origin-provider vmware_vsphere
    --destination-provider openstack --origin-connection-secret $SECRET_REF
    --instance VM1 --target-environment "$TARGET_ENV"

List all migrations
-------------------

The following command retrieves a list of all migrations, including their
status::

    coriolis migration list

Show migration details
----------------------

Migrations can be fairly long running tasks. This command is very useful to
retrieve the current status and all progress updates::

    coriolis migration show <migration_id>

Cancel a migration
------------------

A pending or running migration can be canceled anytime::

    coriolis migration cancel <migration_id>

Delete a migation
-----------------

Only migrations in pending or error state can be deleted. Running migrations
need to be first cancelled::

    coriolis migration delete <migration_id>


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

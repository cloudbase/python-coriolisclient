""" Module showcasing various perations for Coriolis endpoints. """

import json

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


OCI_CONNECTION_INFO = {
    "region": "eu-frankfurt-1",
    "tenancy": "<tenancy OCID>",
    "user": "<user OCID>",
    "private_key_data": "<data of private key>",
    "private_key_passphrase": "<key passphrase>"
}


def get_schema_for_plugin(coriolis, platform_type, schema_type):
    """ Returns a JSON schema detailing params expected by a given plugin.

    :param platform_type: type of platform (e.g. 'openstack', 'oci', 'azure')
    :param schema_type: schema type(e.g. 'connection', 'source', 'destination')
    :return: dict() containing the requrested JSON schema
    """
    provider_schema_type_map = {
        "destination": 1,
        "source": 2,
        "connection": 16
    }

    return coriolis.providers.schemas_list(
        platform_type, provider_schema_type_map[schema_type]).as_dict()


def store_barbican_secret_for_coriolis(
        barbican, secret_info, name='Coriolis Secret'):
    """ Stores secret connection info in Barbican for Coriolis.

    :param barbican: barbican_client.Client instance
    :param secret_info: secret info to store
    :return: the HREF (URL) of the newly-created Barbican secret
    """
    payload = json.dumps(secret_info)

    secret = barbican.secrets.create(
        name=name, payload=payload,
        payload_content_type='application/json')
    secret_href = secret.store()

    return secret_href


def create_endpoint(coriolis, name, platform_type, connection_info,
                    barbican=None, description=''):
    """ Creates and endpoint with the given parameters.

    :param platform_type: type of platform (e.g. 'openstack', 'oci', 'azure')
    :param connection_info: connection info for the given platform
    :param barbican: barbican_client.Client instance for optionally storing
                     the connection info in a Barbican Secret.
    :return: new coriolisclient.v1.Endpoint instance
    """
    # check provider type is installed server-side:
    providers_dict = coriolis.providers.list().as_dict()
    if platform_type not in providers_dict:
        raise ValueError(
            'platform_type must be one of %s' % providers_dict.keys())

    # if Barbican is available, store the connection info in it:
    if barbican:
        secret_href = store_barbican_secret_for_coriolis(
            barbican, connection_info, name='Coriolis Endpoint %s' % name)
        connection_info = {'secret_href': secret_href}

    # create the endpoint:
    endpoint = coriolis.endpoints.create(
        name, platform_type, connection_info, description)

    return endpoint


def get_endpoint_connection_info(coriolis, barbican, endpoint):
    """ Returns the connection info for the given endpoint. """
    endpoint = coriolis.endpoints.get(endpoint)

    if 'secret_href' not in endpoint.connection_info:
        # this endpoint is not using Barbican for secret storage:
        return endpoint.connection_info

    secret = barbican.secrets.get(endpoint.connection_info['secret_href'])

    return json.loads(secret.payload)


def validate_endpoint(coriolis, endpoint, raise_on_error=True):
    """ Validates the given Coriolis endpoint.
    :param endpoint: endpoint object or ID
    :return: (bool, str) tuple containing the result and possible errors
    """
    is_valid, error_msg = coriolis.endpoints.validate_connection(endpoint)

    if raise_on_error and not is_valid:
        raise Exception("Endpoint validation failed: %s" % error_msg)

    return (is_valid, error_msg)


def get_replicas_for_endpoint(coriolis, endpoint,
                              as_source=True, as_target=True):
    """ Returns all Replicas with the given endpoint as source/target. """
    endpoint = coriolis.endpoints.get(endpoint)

    found = []
    for replica in coriolis.replicas.list():
        if as_source and replica.origin_endpoint_id == endpoint.id:
            found.append(replica)

        if as_target and replica.destination_endpoint_id == endpoint.id:
            found.append(replica)

    return found


def delete_endpoint(coriolis, endpoint, force=False):
    """ Removes a given endpoint object/ID. """
    if not force and get_replicas_for_endpoint(coriolis, endpoint):
        raise Exception('Endpoint still has existing Replicas associated.')

    coriolis.endpoints.delete(endpoint)


def main():
    session = ksession.Session(
        auth=v3.Password(**CORIOLIS_CONNECTION_INFO))

    coriolis = coriolis_client.Client(session=session)
    barbican = barbican_client.Client(session=session)

    # create the endppoint:
    endpoint = create_endpoint(
        coriolis, "Coriolis Testing Endpoint", "oci", OCI_CONNECTION_INFO,
        barbican=barbican, description="Created by Coriolis sample scripts")

    # ensure endpoint is valid:
    validate_endpoint(coriolis, endpoint, raise_on_error=True)

    # print endpoint connection info:
    endpoint_connection_info = get_endpoint_connection_info(
        coriolis, barbican, endpoint)
    print("Endpoint '%s' connection info is: %s" % (
        endpoint.id, endpoint_connection_info))

    # see all Replicas away from the endpoint:
    endpoint_replicas = get_replicas_for_endpoint(
        coriolis, endpoint, as_source=True, as_target=False)
    print(
        "Endpoint '%s' is used as a source for the following Replicas: %s" % (
            endpoint.id, [replica.id for replica in endpoint_replicas]))

    # delete the endpoint:
    delete_endpoint(coriolis, endpoint, force=True)

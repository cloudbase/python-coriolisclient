from keystoneauth1 import adapter

from coriolisclient.v1 import migrations


_DEFAULT_SERVICE_TYPE = 'migration'
_DEFAULT_SERVICE_INTERFACE = 'public'
_DEFAULT_API_VERSION = 'v1'


class _HTTPClient(adapter.Adapter):
    def __init__(self, session, **kwargs):
        kwargs.setdefault('interface', _DEFAULT_SERVICE_INTERFACE)
        kwargs.setdefault('service_type', _DEFAULT_SERVICE_TYPE)
        kwargs.setdefault('version', _DEFAULT_API_VERSION)

        super(_HTTPClient, self).__init__(session, **kwargs)


class Client(object):
    def __init__(self, session=None, *args, **kwargs):
        httpclient = _HTTPClient(session=session, *args, **kwargs)
        self.migrations = migrations.MigrationManager(httpclient)

from coriolisclient import base


class ProgressUpdate(base.Resource):
    pass


class Task(base.Resource):
    @property
    def progress_updates(self):
        if not self._loaded or self._info.get('progress_updates') is None:
            self.get()
        return [ProgressUpdate(None, d, loaded=True) for d in
                self._info.get('progress_updates', [])]


class MigrationEndpoint(base.Resource):
    pass


class Origin(MigrationEndpoint):
    pass


class Destination(MigrationEndpoint):
    pass


class Migration(base.Resource):
    _tasks = None

    @property
    def origin(self):
        return Origin(None, self._info.get("origin"), loaded=True)

    @property
    def destination(self):
        return Destination(None, self._info.get("destination"), loaded=True)

    @property
    def tasks(self):
        if not self._loaded or self._info.get('tasks') is None:
            self.get()
        return [Task(None, d, loaded=True) for d in
                self._info.get('tasks', [])]

    def cancel(self):
        self.client.cancel(self)


class MigrationManager(base.BaseManager):
    resource_class = Migration

    def __init__(self, api):
        super(MigrationManager, self).__init__(api)

    def list(self):
        return self._list('/migrations', 'migrations')

    def get(self, migration):
        return self._get('/migrations/%s' % base.getid(migration), 'migration')

    def create(self, origin_type, origin_connection_info, destination_type,
               destination_connection_info, target_environment, instances):
        data = {"migration": {
            "origin": {
                "type": origin_type,
                "connection_info": origin_connection_info,
                },
            "destination": {
                "type": destination_type,
                "connection_info": destination_connection_info,
                "target_environment": target_environment,
                },
            "instances": instances,
            }
        }
        return self._post('/migrations', data, 'migration')

    def delete(self, migration):
        return self._delete('/migrations/%s' % base.getid(migration))

    def cancel(self, migration):
        return self.client.post(
            '/migrations/%s/actions' % base.getid(migration),
            json={'cancel': None})

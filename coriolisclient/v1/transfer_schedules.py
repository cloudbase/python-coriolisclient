# Copyright (c) 2017 Cloudbase Solutions Srl
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

from six.moves.urllib import parse as urlparse

from coriolisclient import base


class TransferSchedule(base.Resource):
    _tasks = None


class TransferScheduleManager(base.BaseManager):
    resource_class = TransferSchedule

    def __init__(self, api):
        super(TransferScheduleManager, self).__init__(api)

    def list(self, transfer, hide_expired=False):
        query = {}
        if hide_expired:
            query["show_expired"] = hide_expired is False
        url = '/transfers/%s/schedules' % base.getid(transfer)
        if query:
            url += "?" + urlparse.urlencode(query)
        return self._list(url, 'schedules')

    def get(self, transfer, schedule):
        return self._get(
            '/transfers/%(transfer_id)s/schedules/%(schedule_id)s' %
            {"transfer_id": base.getid(transfer),
             "schedule_id": base.getid(schedule)},
            'schedule')

    def create(self, transfer, schedule, enabled, expiration_date,
               shutdown_instance):
        data = {
            "schedule": schedule,
            "enabled": enabled,
            "shutdown_instance": shutdown_instance,
        }
        if expiration_date:
            data["expiration_date"] = self._format_rfc3339_datetime(
                expiration_date)
        return self._post(
            '/transfers/%s/schedules' % base.getid(transfer), data, 'schedule')

    def update(self, transfer_id, schedule_id, updated_values):
        expiration_date = updated_values.get("expiration_date")
        if expiration_date:
            updated_values = updated_values.copy()
            updated_values["expiration_date"] = self._format_rfc3339_datetime(
                expiration_date)

        return self._put(
            '/transfers/%(transfer_id)s/schedules/%(schedule_id)s' % {
                "transfer_id": base.getid(transfer_id),
                "schedule_id": base.getid(schedule_id)},
            updated_values, 'schedule')

    def delete(self, transfer, schedule):
        return self._delete(
            '/transfers/%(transfer_id)s/schedules/%(schedule_id)s' %
            {"transfer_id": base.getid(transfer),
             "schedule_id": base.getid(schedule)})

    @staticmethod
    def _format_rfc3339_datetime(dt):
        # NOTE(gsamfira): isoformat requires a Z at the end to make
        # it strict-rfc3339 compliant. The Z (Zulu/Zero offset) denotes
        # UTC time.
        return "%sZ" % dt.isoformat()

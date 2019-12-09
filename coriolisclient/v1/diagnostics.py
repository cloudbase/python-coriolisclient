# Copyright (c) 2019 Cloudbase Solutions Srl
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

from coriolisclient import base


class Diagnostics(base.Resource):
    pass


class DiagnosticsManager(base.BaseManager):
    resource_class = Diagnostics

    def __init__(self, api):
        super(DiagnosticsManager, self).__init__(api)

    def get(self):
        return self._list('/diagnostics', 'diagnostics')

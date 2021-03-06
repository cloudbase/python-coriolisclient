# Copyright (c) 2016 Cloudbase Solutions Srl
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

import base64
import json

from coriolisclient import base
from coriolisclient import exceptions


class ProgressUpdate(base.Resource):
    pass


class Task(base.Resource):
    @property
    def progress_updates(self):
        if not self._loaded or self._info.get('progress_updates') is None:
            self.get()
        return [ProgressUpdate(None, d, loaded=True) for d in
                self._info.get('progress_updates', [])]


class TasksExecution(base.Resource):
    pass


class SourceEnvironment(base.Resource):
    pass


class DestinationEnvironment(base.Resource):
    pass


class TransferResult(base.Resource):
    pass


def encode_base64_param(param, is_json=False):
    try:
        if is_json:
            param = json.dumps(param)
        return base64.urlsafe_b64encode(param.encode()).decode()
    except Exception as ex:
        raise exceptions.CoriolisException(str(ex))

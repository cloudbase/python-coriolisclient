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

MIGRATION_STATUS_RUNNING = "RUNNING"
MIGRATION_STATUS_COMPLETED = "COMPLETED"
MIGRATION_STATUS_ERROR = "ERROR"

TASK_STATUS_PENDING = "PENDING"
TASK_STATUS_RUNNING = "RUNNING"
TASK_STATUS_COMPLETED = "COMPLETED"
TASK_STATUS_ERROR = "ERROR"
TASK_STATUS_CANCELED = "CANCELED"

TASK_TYPE_EXPORT_INSTANCE = "EXPORT_INSTANCE"
TASK_TYPE_IMPORT_INSTANCE = "IMPORT_INSTANCE"

TASK_EVENT_INFO = "INFO"
TASK_EVENT_WARNING = "WARNING"
TASK_EVENT_ERROR = "ERROR"


OS_TYPE_BSD = "bsd"
OS_TYPE_LINUX = "linux"
OS_TYPE_OS_X = "osx"
OS_TYPE_SOLARIS = "solaris"
OS_TYPE_WINDOWS = "windows"
OS_TYPE_OTHER = "other"
OS_TYPE_UNKNOWN = "unknown"

OS_LIST = [
    OS_TYPE_BSD,
    OS_TYPE_LINUX,
    OS_TYPE_OS_X,
    OS_TYPE_SOLARIS,
    OS_TYPE_WINDOWS,
    OS_TYPE_OTHER,
    OS_TYPE_UNKNOWN,
]
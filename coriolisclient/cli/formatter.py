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


class EntityFormatter(object):
    """Base Mixin class providing functions that format entities for display.

    Must be used in conjunction with a Formatter mixin that provides
    the function _get_formatted_data().
    """

    def _get_sorted_list(self, obj_list):
        return obj_list

    def list_objects(self, obj_list):
        columns = []
        data = (self._get_generic_data(obj) for obj in
                self._get_sorted_list(obj_list))
        if obj_list:
            columns = self._get_generic_columns()
        return columns, data

    def _get_generic_data(self, obj):
        return self._get_formatted_data(obj)

    def _get_generic_columns(self):
        return self.columns

    def get_formatted_entity(self, obj):
        return self.columns, self._get_formatted_data(obj)

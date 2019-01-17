# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 OpenStack Foundation
# Copyright 2012 Grid Dynamics
# Copyright 2013 OpenStack Foundation
# Copyright 2016 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy

import six

from oslo_utils import strutils


def getid(obj):
    """Return id if argument is a Resource.
    Abstracts the common pattern of allowing both an object or an object's ID
    (UUID) as a parameter when dealing with relationships.
    """
    try:
        if obj.uuid:
            return obj.uuid
    except AttributeError:
        pass
    try:
        return obj.id
    except AttributeError:
        return obj


class Resource(object):
    """Base class for OpenStack resources (tenant, user, etc.).

    This is pretty much just a bag for attributes.
    """

    HUMAN_ID = False
    NAME_ATTR = 'name'

    def __init__(self, manager, info, loaded=False):
        """Populate and bind to a manager.

        :param manager: BaseManager object
        :param info: dictionary representing resource attributes
        :param loaded: prevent lazy-loading if set to True
        """
        self.manager = manager
        self._info = info
        self._add_details(info)
        self._loaded = loaded

    def __repr__(self):
        reprkeys = sorted(k
                          for k in self.__dict__.keys()
                          if k[0] != '_' and k != 'manager')
        info = ", ".join("%s=%s" % (k, getattr(self, k)) for k in reprkeys)
        return "<%s %s>" % (self.__class__.__name__, info)

    @property
    def human_id(self):
        """Human-readable ID which can be used for bash completion."""
        if self.HUMAN_ID:
            name = getattr(self, self.NAME_ATTR, None)
            if name is not None:
                return strutils.to_slug(name)
        return None

    def _add_details(self, info):
        for (k, v) in six.iteritems(info):
            try:
                setattr(self, k, v)
                self._info[k] = v
            except AttributeError:
                # In this case we already defined the attribute on the class
                pass

    def __getattr__(self, k):
        if k not in self.__dict__:
            # NOTE(bcwaldon): disallow lazy-loading if already loaded once
            if not self.is_loaded():
                self.get()
                return self.__getattr__(k)

            raise AttributeError(k)
        else:
            return self.__dict__[k]

    def get(self):
        """Support for lazy loading details.

        Some clients, such as novaclient have the option to lazy load the
        details, details which can be loaded with this function.
        """
        # set_loaded() first ... so if we have to bail, we know we tried.
        self.set_loaded(True)
        if not hasattr(self.manager, 'get'):
            return

        new = self.manager.get(self.id)
        if new:
            self._add_details(new._info)

    def __eq__(self, other):
        if not isinstance(other, Resource):
            return NotImplemented
        # two resources of different types are not equal
        if not isinstance(other, self.__class__):
            return False
        return self._info == other._info

    def is_loaded(self):
        return self._loaded

    def set_loaded(self, val):
        self._loaded = val

    def to_dict(self):
        return copy.deepcopy(self._info)


class BaseManager(object):
    """Basic manager type providing common operations.
    Managers interact with a particular type of API (servers, flavors, images,
    etc.) and provide CRUD operations for them.
    """
    resource_class = None

    def __init__(self, client):
        """Initializes BaseManager with `client`.
        :param client: instance of BaseClient descendant for HTTP requests
        """
        super(BaseManager, self).__init__()
        self.client = client

    def _list(self, url, response_key=None, obj_class=None, json=None,
              values_key='values'):
        """List the collection.
        :param url: a partial URL, e.g., '/servers'
        :param response_key: the key to be looked up in response dictionary,
            e.g., 'servers'. If response_key is None - all response body
            will be used.
        :param obj_class: class for constructing the returned objects
            (self.resource_class will be used by default)
        :param json: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        """
        if json:
            body = self.client.post(url, json=json).json()
        else:
            body = self.client.get(url).json()

        if obj_class is None:
            obj_class = self.resource_class

        data = body[response_key] if response_key is not None else body
        # NOTE(ja): keystone returns values as list as {'values': [ ... ]}
        #           unlike other services which just return the list...
        try:
            data = data[values_key]
        except (KeyError, TypeError):
            pass

        return [obj_class(self, res, loaded=True) for res in data if res]

    def _get(self, url, response_key=None):
        """Get an object from collection.
        :param url: a partial URL, e.g., '/servers'
        :param response_key: the key to be looked up in response dictionary,
            e.g., 'server'. If response_key is None - all response body
            will be used.
        """
        body = self.client.get(url).json()
        data = body[response_key] if response_key is not None else body
        return self.resource_class(self, data, loaded=True)

    def _post(self, url, json, response_key=None, return_raw=False):
        """Create an object.
        :param url: a partial URL, e.g., '/servers'
        :param json: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        :param response_key: the key to be looked up in response dictionary,
            e.g., 'server'. If response_key is None - all response body
            will be used.
        :param return_raw: flag to force returning raw JSON instead of
            Python object of self.resource_class
        """
        body = self.client.post(url, json=json).json()
        data = body[response_key] if response_key is not None else body
        if return_raw:
            return data
        return self.resource_class(self, data)

    def _put(self, url, json=None, response_key=None):
        """Update an object with PUT method.
        :param url: a partial URL, e.g., '/servers'
        :param json: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        :param response_key: the key to be looked up in response dictionary,
            e.g., 'servers'. If response_key is None - all response body
            will be used.
        """
        resp = self.client.put(url, json=json)
        # PUT requests may not return a body
        if resp.content:
            body = resp.json()
            if response_key is not None:
                return self.resource_class(self, body[response_key])
            else:
                return self.resource_class(self, body)

    def _patch(self, url, json=None, response_key=None):
        """Update an object with PATCH method.
        :param url: a partial URL, e.g., '/servers'
        :param json: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        :param response_key: the key to be looked up in response dictionary,
            e.g., 'servers'. If response_key is None - all response body
            will be used.
        """
        body = self.client.patch(url, json=json).json()
        if response_key is not None:
            return self.resource_class(self, body[response_key])
        else:
            return self.resource_class(self, body)

    def _delete(self, url):
        """Delete an object.
        :param url: a partial URL, e.g., '/servers/my-server'
        """
        return self.client.delete(url)

# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

"""Defines base class for all tests."""

from oslotest import base


class CoriolisBaseTestCase(base.BaseTestCase):

    def setUp(self):
        super(CoriolisBaseTestCase, self).setUp()

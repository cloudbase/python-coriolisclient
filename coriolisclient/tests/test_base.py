# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

"""Defines base class for all tests."""

from oslotest import base
from oslotest import mock_fixture

# NOTE(claudiub): this needs to be called before any mock.patch calls are
# being done, and especially before any other test classes load. This fixes
# the mock.patch autospec issue:
# https://github.com/testing-cabal/mock/issues/396
mock_fixture.patch_mock_module()


class CoriolisBaseTestCase(base.BaseTestCase):

    def setUp(self):
        super(CoriolisBaseTestCase, self).setUp()

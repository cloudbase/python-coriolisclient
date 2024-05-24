# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import ddt
import logging
import os
from unittest import mock

from cliff import app
from cliff import commandmanager
from keystoneauth1 import loading
from keystoneauth1 import session

from coriolisclient.cli import shell
from coriolisclient import client
from coriolisclient import exceptions
from coriolisclient.tests import test_base


class CustomMock(mock.MagicMock):
    def __getattr__(self, name):
        return None


@ddt.ddt
class CoriolisTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Shell App."""

    def setUp(self):
        super(CoriolisTestCase, self).setUp()
        self.coriolis = shell.Coriolis()

    @ddt.data(
        {
            "args": {
                "os_project_id": "mock_os_project_id",
                "os_project_name": "mock_os_project_name",
                "os_project_domain_name": "mock_os_project_domain_name",
                "os_project_domain_id": "mock_os_project_domain_id",
                "os_tenant_id": "mock_os_tenant_id",
                "os_tenant_name": "mock_os_tenant_name"
            },
            "api_version": '3',
            "raise_exc": False,
            "expected_result": True
        },
        {
            "args": {
                "os_project_id": "mock_os_project_id",
                "os_project_name": "mock_os_project_name",
                "os_project_domain_name": "mock_os_project_domain_name",
                "os_project_domain_id": "mock_os_project_domain_id",
            },
            "api_version": '3',
            "raise_exc": False,
            "expected_result": True
        },
        {
            "args": {
                "os_tenant_id": "mock_os_tenant_id",
                "os_tenant_name": "mock_os_tenant_name"
            },
            "api_version": '2',
            "raise_exc": False,
            "expected_result": True
        },
        {
            "raise_exc": False,
            "expected_result": False
        },
        {
            "api_version": '2',
            "raise_exc": True,
        }
    )
    def test_check_auth_arguments(self, data):
        args = CustomMock()
        for key, value in data.get("args", {}).items():
            setattr(args, key, value)
        expected_result = data.get("expected_result")

        if expected_result is not None:
            result = self.coriolis.check_auth_arguments(
                args,
                api_version=data.get("api_version", None),
                raise_exc=data.get("raise_exc", False)
            )

            self.assertEqual(
                expected_result,
                result
            )
        else:
            self.assertRaises(
                exceptions.CoriolisException,
                self.coriolis.check_auth_arguments,
                args,
                data.get("api_version", None),
                raise_exc=data.get("raise_exc", False)
            )

    @ddt.data(
        {
            "args": {
                "os_tenant_id": "mock_os_tenant_id",
                "os_tenant_name": "mock_os_tenant_name"
            },
            "kwargs": {
                "os_tenant_name": "new_mock_os_tenant_name"
            },
            "api_version": '2',
            "auth_type": 'token',
            "auth_fun": 'keystoneauth1.identity.v2.Token'
        },
        {
            "args": {
                "os_tenant_id": "mock_os_tenant_id",
                "os_tenant_name": "mock_os_tenant_name"
            },
            "kwargs": {
                "os_tenant_name": "new_mock_os_tenant_name"
            },
            "api_version": '2',
            "auth_fun": 'keystoneauth1.identity.v2.Password'
        },
        {
            "args": {
                "os_project_id": "mock_os_project_id",
                "os_project_name": "mock_os_project_name",
                "os_project_domain_name": "mock_os_project_domain_name",
                "os_project_domain_id": "mock_os_project_domain_id",
            },
            "kwargs": {
                "os_project_domain_name": "new_mock_os_project_domain_name",
                "os_project_domain_id": "new_mock_os_project_domain_id",
            },
            "api_version": '3',
            "auth_type": 'token',
            "auth_fun": 'keystoneauth1.identity.v3.Token'
        },
        {
            "args": {
                "os_project_id": "mock_os_project_id",
                "os_project_name": "mock_os_project_name",
                "os_project_domain_name": "mock_os_project_domain_name",
                "os_project_domain_id": "mock_os_project_domain_id",
            },
            "kwargs": {
                "os_project_domain_name": "new_mock_os_project_domain_name",
                "os_project_domain_id": "new_mock_os_project_domain_id",
            },
            "auth_fun": 'keystoneauth1.identity.v3.Password',
            "err_msg": True
        }
    )
    @mock.patch.object(session, 'Session')
    @mock.patch.object(shell.Coriolis, 'build_kwargs_based_on_version')
    @mock.patch.object(shell.Coriolis, 'check_auth_arguments')
    def test_create_keystone_session(
        self,
        data,
        mock_check_auth_arguments,
        mock_build_kwargs_based_on_version,
        mock_Session
    ):
        args = CustomMock()
        for key, value in data.get("args", {}).items():
            setattr(args, key, value)
        kwargs = data.get("kwargs", {})
        ret_args = data.get("args", {})
        mock_build_kwargs_based_on_version.return_value = ret_args.copy()
        expected_kwargs = ret_args.copy()
        expected_kwargs.update(kwargs.copy())
        mock_stderr = mock.Mock()
        self.coriolis.stderr = mock_stderr

        auth_fun = data['auth_fun']
        with mock.patch(auth_fun) as mock_auth:
            result = self.coriolis.create_keystone_session(
                args,
                api_version=data.get("api_version", None),
                kwargs_dict=kwargs.copy(),
                auth_type=data.get("auth_type", None)
            )

            self.assertEqual(
                mock_Session.return_value,
                result
            )
            mock_check_auth_arguments.assert_called_once_with(
                args,
                data.get("api_version", None),
                raise_exc=True
            )
            mock_build_kwargs_based_on_version.assert_called_once_with(
                args,
                data.get("api_version", None)
            )
            mock_auth.assert_called_once_with(**expected_kwargs)

    @ddt.data(
        {
            "args": {
                "no_auth": "mock_no_auth",
                "os_auth_url": "mock_os_auth_url"
            }
        },
        {
            "args": {
                "no_auth": "mock_no_auth",
                "endpoint": "mock_endpoint"
            }
        },
        {
            "args": {
                "no_auth": "mock_no_auth",
                "endpoint": "mock_endpoint",
                "os_tenant_id": "mock_os_tenant_id"
            },
            "call_args": {
                "endpoint": "mock_endpoint",
                "project_id": "mock_os_tenant_id",
                "verify": True
            }
        },
        {
            "args": {
                "os_auth_token": "mock_os_auth_token"
            }
        },
        {
            "args": {
                "os_auth_token": "mock_os_auth_token",
                "os_auth_url": "mock_os_auth_url",
                "os_tenant_id": "mock_os_tenant_id",
                "endpoint": "mock_endpoint"
            },
            "call_args": {
                "endpoint": "mock_endpoint"
            },
            "create_keystone_session_args": {
                "auth_url": "mock_os_auth_url",
                "token": "mock_os_auth_token"
            },
            "auth_type": "token"
        },
        {
            "args": {
                "os_auth_url": "mock_os_auth_url",
                "os_password": "mock_os_password",
                "os_user_id": "mock_os_user_id",
                "os_username": "mock_os_username",
                "endpoint": "mock_endpoint"
            },
            "call_args": {
                "endpoint": "mock_endpoint"
            },
            "create_keystone_session_args": {
                "auth_url": "mock_os_auth_url",
                "password": "mock_os_password",
                "user_id": "mock_os_user_id",
                "username": "mock_os_username",
            },
            "auth_type": "password"
        },
        {}
    )
    @mock.patch.object(shell.Coriolis, 'create_keystone_session')
    @mock.patch.object(client, 'Client')
    @mock.patch.object(shell.Coriolis, '_get_endpoint_filter_kwargs')
    def test_create_client(
        self,
        data,
        mock_get_endpoint_filter_kwargs,
        mock_Client,
        mock_create_keystone_session
    ):
        args = CustomMock()
        args.os_identity_api_version = mock.sentinel.os_identity_api_version
        for key, value in data.get("args", {}).items():
            setattr(args, key, value)
        endpoint_filter_kwargs = {"filter_arg": "mock_filter_arg"}
        mock_get_endpoint_filter_kwargs.return_value = endpoint_filter_kwargs
        call_args = data.get("call_args")
        create_keystone_session_args = data.get("create_keystone_session_args")

        if call_args is not None:
            call_args.update(endpoint_filter_kwargs)

            result = self.coriolis.create_client(args)

            self.assertEqual(
                mock_Client.return_value,
                result
            )

            if args.no_auth:
                mock_Client.assert_called_once_with(**call_args)
            else:
                mock_create_keystone_session.assert_called_once_with(
                    args,
                    mock.sentinel.os_identity_api_version,
                    create_keystone_session_args,
                    auth_type=data["auth_type"]
                )
                mock_Client.assert_called_once_with(
                    session=mock_create_keystone_session.return_value,
                    **call_args
                )
        else:
            self.assertRaises(
                exceptions.CoriolisException,
                self.coriolis.create_client,
                args
            )

    def test_build_kwargs_based_on_version(self):
        args = CustomMock()
        args.os_project_id = mock.sentinel.os_project_id
        args.os_tenant_name = mock.sentinel.os_tenant_name

        result = self.coriolis.build_kwargs_based_on_version(args)

        self.assertEqual(
            {'project_id': mock.sentinel.os_project_id},
            result
        )

        api_version = '2'

        result = self.coriolis.build_kwargs_based_on_version(args, api_version)

        self.assertEqual(
            {'tenant_name': mock.sentinel.os_tenant_name},
            result
        )

    def test_get_endpoint_filter_kwargs(
        self
    ):
        args = mock.Mock()
        args.interface = mock.sentinel.interface
        args.service_type = mock.sentinel.service_type
        args.service_name = mock.sentinel.service_name
        args.coriolis_api_version = mock.sentinel.coriolis_api_version
        args.region_name = mock.sentinel.region_name
        expected_result = {
            "interface": mock.sentinel.interface,
            "service_type": mock.sentinel.service_type,
            "service_name": mock.sentinel.service_name,
            "region_name": mock.sentinel.region_name,
            "version": mock.sentinel.coriolis_api_version,
        }

        result = self.coriolis._get_endpoint_filter_kwargs(args)

        self.assertEqual(
            expected_result,
            result
        )

    @mock.patch.object(shell.Coriolis, '_env')
    @mock.patch.object(loading, 'register_session_argparse_arguments')
    @mock.patch.object(app.App, 'build_option_parser')
    def test_build_option_parser(
        self,
        mock_build_option_parser,
        mock_register_session_argparse_arguments,
        *_
    ):
        result = self.coriolis.build_option_parser(
            mock.sentinel.description, mock.sentinel.version)

        self.assertEqual(
            mock_build_option_parser.return_value,
            result
        )
        mock_build_option_parser.assert_called_once_with(
            mock.sentinel.description, mock.sentinel.version, None)
        mock_register_session_argparse_arguments.assert_called_once_with(
            mock_build_option_parser.return_value)

    def test_env(self):
        result = self.coriolis._env(
            "HOME", mock.sentinel.default)

        self.assertEqual(
            os.environ.get("HOME"),
            result
        )

    @mock.patch.object(shell.Coriolis, 'create_client')
    def test_prepare_to_run_command(self, mock_create_client):
        cmd = mock.Mock()
        cmd.auth_required = True
        self.coriolis.options = mock.sentinel.options

        self.coriolis.prepare_to_run_command(cmd)

        self.assertEqual(
            mock_create_client.return_value,
            self.coriolis.client_manager.coriolis
        )
        mock_create_client.assert_called_once_with(mock.sentinel.options)

    @mock.patch.object(app.App, 'run')
    def test_run(self, mock_run):
        mock_stderr = mock.Mock()
        mock_parser = mock.Mock()
        self.coriolis.stderr = mock_stderr
        self.coriolis.parser = mock_parser

        result = self.coriolis.run(None)

        self.assertEqual(
            1,
            result
        )
        mock_stderr.write.assert_called_once_with(
            mock_parser.format_usage.return_value)
        mock_run.assert_not_called()

        mock_stderr.reset_mock()
        mock_parser.reset_mock()

        result = self.coriolis.run(mock.sentinel.argv)

        self.assertEqual(
            mock_run.return_value,
            result
        )
        mock_parser.format_usage.assert_not_called()


class ShellTestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis Shell."""

    def test_setup_logging(self):
        shell._setup_logging()
        self.assertEqual(
            (
                logging.WARNING,
                logging.ERROR
            ),
            (
                logging.getLogger("requests").level,
                logging.getLogger("keystoneclient").level
            )
        )

    @mock.patch.object(shell.Coriolis, 'run')
    @mock.patch.object(commandmanager, 'CommandManager')
    @mock.patch.object(app.App, '__init__')
    @mock.patch.object(shell, '_setup_logging')
    def test_main(
        self,
        mock_setup_logging,
        mock__init__,
        mock_CommandManager,
        mock_run
    ):
        result = shell.main(mock.sentinel.argv)

        self.assertEqual(
            mock_run.return_value,
            result
        )
        mock_setup_logging.assert_called_once()
        mock__init__.assert_called_once_with(
            description=mock.ANY,
            version=mock.ANY,
            command_manager=mock_CommandManager.return_value,
            deferred_help=True
        )
        mock_CommandManager.assert_called_once_with("coriolis.v1")
        mock_run.assert_called_once_with(mock.sentinel.argv)

# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

import ddt
import logging
import os
from unittest import mock

from cliff import app
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

    @ddt.file_data('data/shell_check_auth_arguments.yml')
    @ddt.unpack
    def test_check_auth_arguments(self, config):
        args = CustomMock()
        if config.get("args"):
            for key, value in config.get("args").items():
                setattr(args, key, value)
        expected_result = config.get("expected_result")

        if expected_result is not None:
            result = self.coriolis.check_auth_arguments(
                args,
                api_version=config.get("api_version", None),
                raise_exc=config.get("raise_exc", False)
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
                api_version=config.get("api_version", None),
                raise_exc=config.get("raise_exc", False)
            )

    @ddt.file_data('data/shell_create_keystone_auth.yml')
    @ddt.unpack
    @mock.patch.object(session, 'Session')
    def test_create_keystone_session(
        self,
        mock_Session,
        config
    ):
        args = CustomMock()
        if config.get("args"):
            for key, value in config.get("args").items():
                setattr(args, key, value)
        kwargs = config.get("kwargs", {})
        expected_kwargs = config.get("expected_kwargs", {})
        mock_stderr = mock.Mock()
        self.coriolis.stderr = mock_stderr

        auth_fun = config['auth_fun']
        with mock.patch(auth_fun) as mock_auth:
            result = self.coriolis.create_keystone_session(
                args,
                api_version=config.get("api_version", None),
                kwargs_dict=kwargs,
                auth_type=config.get("auth_type", None),
                verify=config.get("verify", True)
            )

            self.assertEqual(
                mock_Session.return_value,
                result
            )
            mock_Session.assert_called_once_with(
                auth=mock_auth.return_value, verify=config.get("verify", True))
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
            "expected_client_kwargs": {
                "endpoint": "mock_endpoint",
                "project_id": "mock_os_tenant_id",
            }
        },
        {
            "args": {
                "os_auth_token": "mock_os_auth_token",
                "os_auth_url": "mock_os_auth_url",
                "os_tenant_id": "mock_os_tenant_id",
                "endpoint": "mock_endpoint",
                "region_name": "mock_region_name"
            },
            "expected_client_kwargs": {
                "endpoint": "mock_endpoint",
                "region_name": "mock_region_name"
            },
            "expected_ks_session_kwargs": {
                "auth_url": "mock_os_auth_url",
                "token": "mock_os_auth_token"
            },
            "auth_type": "token"
        },
        {
            "args": {
                "os_auth_token": "mock_os_auth_token",
                "os_auth_url": "mock_os_auth_url",
                "os_tenant_id": "mock_os_tenant_id",
                "endpoint": "mock_endpoint",
                "region_name": "mock_region_name",
                "insecure": True
            },
            "expected_client_kwargs": {
                "endpoint": "mock_endpoint",
                "region_name": "mock_region_name"
            },
            "expected_ks_session_kwargs": {
                "auth_url": "mock_os_auth_url",
                "token": "mock_os_auth_token"
            },
            "auth_type": "token",
            "verify": False
        },
        {
            "args": {
                "os_auth_token": "mock_os_auth_token",
                "os_auth_url": "mock_os_auth_url",
                "os_tenant_id": "mock_os_tenant_id",
                "endpoint": "mock_endpoint",
                "region_name": "mock_region_name",
                "insecure": True,
                "os_cacert": "mock_os_cacert"
            },
            "expected_client_kwargs": {
                "endpoint": "mock_endpoint",
                "region_name": "mock_region_name"
            },
            "expected_ks_session_kwargs": {
                "auth_url": "mock_os_auth_url",
                "token": "mock_os_auth_token"
            },
            "auth_type": "token",
            "verify": "mock_os_cacert"
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
            "expected_client_kwargs": {
                "endpoint": "mock_endpoint"
            },
            "expected_ks_session_kwargs": {
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
            "expected_client_kwargs": {
                "endpoint": "mock_endpoint"
            },
            "expected_ks_session_kwargs": {
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
    def test_create_client(
        self,
        data,
        mock_Client,
        mock_create_ks_session
    ):
        args = CustomMock()
        args.os_identity_api_version = mock.sentinel.os_identity_api_version
        for key, value in data.get("args", {}).items():
            setattr(args, key, value)
        expected_client_kwargs = data.get("expected_client_kwargs")
        expected_ks_session_kwargs = data.get("expected_ks_session_kwargs", {})

        if expected_client_kwargs is not None:
            result = self.coriolis.create_client(args)
            self.assertEqual(
                result, mock_Client.return_value)
            if expected_ks_session_kwargs:
                mock_Client.assert_called_once_with(
                    session=mock_create_ks_session.return_value,
                    **expected_client_kwargs,
                    verify=data.get("verify", True))
                mock_create_ks_session.assert_called_once_with(
                    args,
                    mock.sentinel.os_identity_api_version,
                    expected_ks_session_kwargs,
                    auth_type=data["auth_type"],
                    verify=data.get("verify", True))
            else:
                mock_Client.assert_called_once_with(
                    **expected_client_kwargs,
                    verify=data.get("verify", True))
        else:
            self.assertRaises(
                exceptions.CoriolisException,
                self.coriolis.create_client,
                args
            )

    @ddt.data(
        {
            "args": {
                "os_project_id": "mock_project_id",
                "os_tenant_name": "mock_tenant_name"
            },
            "api_version": 3,
            "expected_kwargs": {
                "tenant_name": "mock_tenant_name"
            }
        },
        {
            "args": {
                "os_project_id": "mock_project_id",
                "os_tenant_name": "mock_tenant_name"
            },
            "api_version": 2,
            "expected_kwargs": {
                "tenant_name": "mock_tenant_name"
            }
        },
        {
            "args": {
                "os_project_id": "mock_project_id",
                "os_tenant_name": "mock_tenant_name"
            },
            "api_version": None,
            "expected_kwargs": {
                "project_id": "mock_project_id"
            }
        },
        {
            "args": {},
            "api_version": None,
            "expected_kwargs": {}
        }
    )
    def test_build_kwargs_based_on_version(self, data):
        args = CustomMock()
        for key, value in data.get("args", {}).items():
            setattr(args, key, value)
        api_version = data["api_version"]

        result = self.coriolis.build_kwargs_based_on_version(
            args, api_version=api_version)

        self.assertEqual(
            data["expected_kwargs"],
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
        os.environ["TEST_ENV"] = "test_value"
        result = self.coriolis._env(
            "TEST_ENV", mock.sentinel.default)

        self.assertEqual(
            "test_value",
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
    def test_main(
        self,
        mock_run
    ):
        result = shell.main(mock.sentinel.argv)

        self.assertEqual(
            mock_run.return_value,
            result
        )
        mock_run.assert_called_once_with(mock.sentinel.argv)

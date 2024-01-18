# -*- coding: utf-8 -*-

"""
Utility module to temporarily set the ``${HOMe}/.aws`` folder, and restore it.
"""

import typing as T
import contextlib

from ..paths import dir_python_lib, dir_aws, path_aws_config, path_aws_credentials


def read_existing() -> T.Tuple[T.Optional[str], T.Optional[str]]:
    if path_aws_config.exists():
        config_content = path_aws_config.read_text()
    else:
        config_content = None
    if path_aws_credentials.exists():
        credentials_content = path_aws_credentials.read_text()
    else:
        credentials_content = None
    return config_content, credentials_content


def write_content(config_content, credentials_content):
    dir_aws.mkdir(parents=True, exist_ok=True)
    if config_content is not None:
        path_aws_config.write_text(config_content)
    if credentials_content is not None:
        path_aws_credentials.write_text(credentials_content)


test_config_content = dir_python_lib.joinpath("tests", ".aws", "config").read_text()
test_credentials_content = dir_python_lib.joinpath(
    "tests", ".aws", "credentials"
).read_text()


class TestHomeAwsFolder:
    def __init__(self):
        self._config_content, self._credentials_content = read_existing()

    def setup(self):
        write_content(test_config_content, test_credentials_content)

    def teardown(self):
        write_content(self._config_content, self._credentials_content)

    @contextlib.contextmanager
    def temp(self):
        try:
            self.setup()
            yield
        finally:
            self.teardown()

test_home_aws_folder = TestHomeAwsFolder()

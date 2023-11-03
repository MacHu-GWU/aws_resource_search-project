# -*- coding: utf-8 -*-

import typing as T
import fire

from awscli_mate.ui import run_ui as run_awscli_mate_ui

from .._version import __version__
from ..ui.main import run_ui as run_ars_ui
from . import which
from . import clear


class ArsCli:
    """
    AWS Resource Search CLI.

    Search AWS resource in terminal, just like you are using AWS Console in web browser.

    You can do things like:

    - open aws console url
    - copy information to clipboard
    - view aws resource details in terminal

    For full documentation, please view https://github.com/MacHu-GWU/aws_resource_search-project

    Usage:

    - ``ars``: enter the AWS resource search interactive UI
    - ``ars -v``: show the version of this tool
    - ``ars -h``: show this help message
    - ``ars ${{sub_command}}``: run the given sub command. See "COMMANDS" section below.
    """

    def __call__(self, version: T.Optional[bool] = None):
        if version:
            print(__version__)
        else:
            run_ars_ui()

    def which(self):
        """
        Show AWS account id, alias, region of the current boto3 session.

        Usage:

        ``ars which``, print the AWS account id, alias, region of the current boto3 session.
        Example::

            $ ars which
            AWS Account ID = 123456789012
            AWS Account Alias = my-aws-account-alias
            AWS Region = us-east-1
        """
        which.main()

    def set_profile(self):
        """
        Set one of your AWS named profile as default profile for ARS UI.

        Usage:

        - ``ars set-profile``, then follow the interactive UI to set the profile.
        - Example: https://github.com/MacHu-GWU/awscli_mate-project#use-awscli_mate-as-a-interactive-cli
        """
        run_awscli_mate_ui()

    def clear(self):
        """
        Clear all index and cache of this App.

        Usage:

        - ``ars clear``: clear all index and cache of this App.
        """
        clear.main()


def run():
    ars_cli = ArsCli()
    fire.Fire(ars_cli)

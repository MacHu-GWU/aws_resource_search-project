# -*- coding: utf-8 -*-

import fire

from .ui.main import run_ui


def main():
    """
    Search AWS resource in terminal, just like you are using AWS Console in web browser.

    You can do things like:

    - open aws console url
    - copy information to clipboard
    - view aws resource details in terminal

    For full documentation, please view https://github.com/MacHu-GWU/aws_resource_search-project
    """
    run_ui()


def run():
    fire.Fire(main)

# -*- coding: utf-8 -*-

import fire

from .ui import run_ui


def main():
    """
    Print the url you can one-click to open it in web browser.

    :param path: the absolute path of the file or folder in your local git repo, if not give, use the current directory.
    """
    run_ui()


def run():
    fire.Fire(main)

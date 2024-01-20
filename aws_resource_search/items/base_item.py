# -*- coding: utf-8 -*-

"""

"""

import typing as T
import dataclasses
from pathlib import Path

import zelfred.api as zf

try:
    import pyperclip
except ImportError:  # pragma: no cover
    pass


@dataclasses.dataclass
class BaseArsItem(zf.Item):
    """
    Base class for all ``zelfred.Item`` subclasses in ``aws_resource_search`` project.
    """

    def open_url_or_print(self, ui: zf.UI, url: str):  # pragma: no cover
        """
        A helper user action method to open a URL in browser or print it to the terminal.

        Sometime user are in a remote shell and doesn't have default web browser.
        Then we print the url instead.

        .. note::

            This method will be used in the ``enter_handler``.
        """
        try:
            zf.open_url(url)
        # if remote shell may not have the ``open`` or ``start`` command
        # then FileNotFoundError will be raised
        except FileNotFoundError as e:
            if "start" in str(e) or "open" in str(e):
                print(
                    f"{ui.terminal.cyan}Your system doesn't support open url in browser, "
                    f"we print it here so you can copy manually.{ui.terminal.normal}"
                )
                print(url)
                ui.need_run_handler = False
                # since the print(url) will mess up the terminal UI,
                # we have to exit the app.
                # if we want to exit the session, based on the source code of
                # ``zf.UI.run_session``, we have to raise either
                # ``KeyboardInterrupt`` or ``zf.exc.EndOfInputError``.
                # either one would work, we intentionally leave both options here
                raise KeyboardInterrupt
                # raise zf.exc.EndOfInputError(selection=self)
            else:
                raise e

    def copy_or_print(self, ui: zf.UI, text: str):  # pragma: no cover
        """
        A helper user action method to copy a text to clipboard or print it to the terminal.

        Sometime user are in a remote shell and cannot use the clipboard.
        Then we print the value instead.

        .. note::

            This method will be used in the ``ctrl_a_handler`` or ``ctrl_w_handler``.
        """
        try:
            pyperclip.copy(text)
        except pyperclip.PyperclipException:
            print(
                f"{ui.terminal.cyan}Your system doesn't support copy to clipboard, "
                f"we print it here so you can copy manually.{ui.terminal.normal}"
            )
            print(text)
            ui.need_run_handler = False
            raise KeyboardInterrupt
            # raise zf.exc.EndOfInputError(selection=self)

    def open_file_or_print(self, ui: zf.UI, path: Path):  # pragma: no cover
        """
        A helper user action method to open a file in default application
        or print it to the terminal.

        Sometime user are in a remote shell and doesn't have an app to open a file.
        Then we print the url instead.

        .. note::

            This method will be used in the ``enter_handler``.
        """
        # try:
        zf.open_file(path)
        # except Exception as e:
        #     print(
        #         f"{ui.terminal.cyan}Your system doesn't support open a file, "
        #         f"we print it here, so you can see it.{ui.terminal.normal}"
        #     )
        #     print(path.read_text())
        #     ui.need_run_handler = False
        #     raise KeyboardInterrupt

    # by default, we don't quit the app when user press any action key
    # ``ui.wait_next_user_input()`` will wait for another user input and
    # skip repainting the UI in the next event loop
    def post_enter_handler(self, ui: zf.UI):  # pragma: no cover
        ui.wait_next_user_input()

    def post_ctrl_a_handler(self, ui: zf.UI):  # pragma: no cover
        ui.wait_next_user_input()

    def post_ctrl_w_handler(self, ui: zf.UI):  # pragma: no cover
        ui.wait_next_user_input()

    def post_ctrl_u_handler(self, ui: zf.UI):  # pragma: no cover
        ui.wait_next_user_input()

    def post_ctrl_p_handler(self, ui: zf.UI):  # pragma: no cover
        ui.wait_next_user_input()


T_ARS_ITEM = T.TypeVar("T_ARS_ITEM", bound=BaseArsItem)

# -*- coding: utf-8 -*-

"""
This module contains functions to manipulate terminal output.
"""

import typing as T
import blessed
from datetime import datetime, timezone

terminal = blessed.Terminal()
"""
The terminal object is a singleton instance of :class:`blessed.Terminal`.
We only create this object once and use it in the 
:func:`~aws_resource_search.ui.main.run_ui`.
"""

term = terminal


def format_shortcut(key: str) -> str:
    """
    Format a keyboard shortcut key. In this project, the color is magenta.
    Example:

        :magenta:`Enter` to open url
    """
    return f"{term.magenta}{key}{term.normal}"


def highlight_text(text: str) -> str:
    """
    Highlight a text with terminal color. In this project, the color is cyan.
    Example:

        this is a very :cyan:`Important message`!
    """
    return f"{term.cyan}{text}{term.normal}"


def format_resource_type(resource_type: str) -> str:
    """
    Format a resource type text with terminal color. In this project,
    the color is blue. Example:

        :blue:`sfn-statemachine`: name = CognitoUserManagement
    """
    return f"{term.green}{resource_type}{term.normal}"


def format_key(key: str) -> str:
    """
    Format a key of key-value-pair text with terminal color. In this project,
    the color is cyan. Example:

        tag :cyan:`environment` = :yellow:`production`
    """
    return highlight_text(key)


def format_value(value: str) -> str:
    """
    Format a value of key-value-pair text with terminal color. In this project,
    the color is yellow. Example:

        tag :cyan:`environment` = :yellow:`production`
    """
    if isinstance(value, datetime):
        value = str(value.astimezone(tz=timezone.utc).replace(microsecond=0))[:19]
    return f"{term.yellow}{value}{term.normal}"


def format_key_value(key: str, value: T.Any) -> str:
    """
    Format a key-value pair text with terminal color. In this project, key is
    in cyan and value is in yellow. Example:

        tag :cyan:`environment` = :yellow:`production`
    """
    if isinstance(value, datetime):
        value = str(value.astimezone(tz=timezone.utc).replace(microsecond=0))[:19]
    return f"{format_key(key)} = {format_value(value)}"


def remove_text_format(text: str) -> str:
    """
    Remove the terminal format from the given text.
    """
    formats = [
        term.cyan,
        term.yellow,
        term.magenta,
        term.blue,
        term.green,
        term.normal,
    ]
    for c in formats:
        text = text.replace(c, "")
    return text


class ShortcutEnum:
    """
    Formatted keyboard shortcuts::

        print("Tap {ShortcutEnum.ENTER} to open url")

    For example, the above code will print:

        Tap :magenta:`Enter` to open url
    """

    TAB = format_shortcut("Tab")
    ENTER = format_shortcut("Enter")
    CTRL_A = format_shortcut("Ctrl A")
    CTRL_W = format_shortcut("Ctrl W")
    CTRL_U = format_shortcut("Ctrl U")
    CTRL_P = format_shortcut("Ctrl P")
    F1 = format_shortcut("F1")


SUBTITLE = (
    f"🌐 {ShortcutEnum.ENTER} to open url, "
    f"📋 {ShortcutEnum.CTRL_A} to copy arn, "
    f"🔗 {ShortcutEnum.CTRL_U} to copy url, "
    f"👀 {ShortcutEnum.CTRL_P} to view details."
)
"""
The subtitle in the zelfred UI.

The default subtitle is the help text to show the user how to interact with the UI.

Example:

🌐 :magenta:`Enter` to open url, 📋 :magenta:`Ctrl A` to copy arn, 🔗 :magenta:`Ctrl U` to copy url, 👀 :magenta:`Ctrl P` to view details."
"""

SHORT_SUBTITLE = (
    f"🌐 {ShortcutEnum.ENTER}, "
    f"📋 {ShortcutEnum.CTRL_A}, "
    f"🔗 {ShortcutEnum.CTRL_U}, "
    f"👀 {ShortcutEnum.CTRL_P}."
)
"""
A shorter version of subtitle.

Example:

🌐 :magenta:`Enter`, 📋 :magenta:`Ctrl A`, 🔗 :magenta:`Ctrl U`, 👀 :magenta:`Ctrl P`."
"""

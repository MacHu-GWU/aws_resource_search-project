# -*- coding: utf-8 -*-

"""
This module contains functions to manipulate terminal output.
"""

import typing as T
import blessed
from datetime import datetime, timezone

terminal = blessed.Terminal()
term = terminal


def format_shortcut(key: str) -> str:
    """
    Format a keyboard shortcut key. In this project, the color is magenta

    Example::

        <magenta>Enter</magenta> to open url
    """
    return f"{term.magenta}{key}{term.normal}"


def highlight_text(text: str) -> str:
    """
    Highlight a text with terminal color. In this project, the color is cyan.

    Example::

        <magenta>Important message</magenta>
    """
    return f"{term.cyan}{text}{term.normal}"


def format_resource_type(resource_type: str) -> str:
    """
    Format a resource type text with terminal color. In this project, the color is blue.

    Example::

        <blue>ec2-instance</blue>
    """
    return f"{term.blue}{resource_type}{term.normal}"


def format_key(key: str) -> str:
    """
    Format a key of key-value-pair text with terminal color. In this project,
    the color is cyan.
    """
    return highlight_text(key)


def format_value(value: str) -> str:
    """
    Format a value of key-value-pair text with terminal color. In this project,
    the color is yellow.
    """
    if isinstance(value, datetime):
        value = str(value.astimezone(tz=timezone.utc).replace(microsecond=0))[:19]
    return f"{term.yellow}{value}{term.normal}"


def format_key_value(key: str, value: T.Any) -> str:
    """
    Format a key-value pair text with terminal color. In this project, key is
    in cyan and value is in yellow.

    For example, if key is "name", value is "alice", then the output will be
    "<cyan>name</cyan> = <yellow>alice</yellow>" (<color> is just for demonstration).
    """
    if isinstance(value, datetime):
        value = str(value.astimezone(tz=timezone.utc).replace(microsecond=0))[:19]
    return f"{format_key(key)} = {format_value(value)}"


class ShortcutEnum:
    """
    Formatted keyboard shortcuts.
    """

    TAB = format_shortcut("Tab")
    ENTER = format_shortcut("Enter")
    CTRL_A = format_shortcut("Ctrl A")
    CTRL_W = format_shortcut("Ctrl W")
    CTRL_U = format_shortcut("Ctrl U")
    CTRL_P = format_shortcut("Ctrl P")

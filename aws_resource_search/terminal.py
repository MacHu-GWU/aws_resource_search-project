# -*- coding: utf-8 -*-

import typing as T
import blessed
from datetime import datetime, timezone

terminal = blessed.Terminal()
term = terminal


def format_shortcut(key: str) -> str:
    return f"{term.magenta}{key}{term.normal}"


def highlight_text(text: str) -> str:
    return f"{term.cyan}{text}{term.normal}"


def format_resource_type(resource_type: str) -> str:
    return f"{term.blue}{resource_type}{term.normal}"


def format_key(key: str) -> str:
    return highlight_text(key)


def format_value(value: str) -> str:
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
    TAB = format_shortcut("Tab")
    ENTER = format_shortcut("Enter")
    CTRL_A = format_shortcut("Ctrl A")
    CTRL_W = format_shortcut("Ctrl W")
    CTRL_P = format_shortcut("Ctrl P")

# -*- coding: utf-8 -*-

import json
from re import findall

__version__ = "0.1.1"

def strip_comment_line_with_symbol(line: str, comment_symbol: str):
    """
    Strip comments from line string.

    :param line: the single line string that you want to strip out comments.
    :param comment_symbol: the comment char that indicate that the comment starts from.
    """
    parts = line.split(comment_symbol)
    counts = [len(findall(r'(?:^|[^"\\]|(?:\\\\|\\")+)(")', part)) for part in parts]
    total = 0
    for nr, count in enumerate(counts):
        total += count
        if total % 2 == 0:
            return comment_symbol.join(parts[: nr + 1]).rstrip()
    else:  # pragma: no cover
        return line.rstrip()


def strip_comments(text: str, comment_symbols=frozenset(("#", "//"))):
    """
    Strip comments from json string.

    :param text: A string containing json with comments started by comment_symbols.
    :param comment_symbols: Iterable of symbols that start a line comment (default # or //).

    :return: The string with the comments removed.
    """
    lines = text.splitlines()
    for k in range(len(lines)):
        for symbol in comment_symbols:
            lines[k] = strip_comment_line_with_symbol(lines[k], symbol)
    return "\n".join(lines)


def json_loads(text: str, ignore_comments: bool = True):
    """
    Load Json from string. But this function can ignore comments.

    Valid commands are::

        # this is a comment
        {
            "a": 1 // this is a comment
        }

    :param text: the json string.
    :param ignore_comments: whether or not to ignore comments.
    """
    if ignore_comments:
        text = strip_comments(text)
    return json.loads(text)

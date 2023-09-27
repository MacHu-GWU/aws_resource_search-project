# -*- coding: utf-8 -*-

"""
In object-oriented programming, the inheritance hierarchy is a pattern where
child objects inherit attributes and methods from parent objects. Similarly,
in configuration management, the global configuration often acts as the
default value, allowing for the possibility of overriding specific values in
environment-specific configurations.

This module implements a simple dialect of JSON that supports inheritance for
better reusability of configuration data. For example, consider the following
config data::

    >>> {
    ...     "_shared": {
    ...         "*.username": "root",
    ...     },
    ...     "server1": {
    ...         "password": "password1",
    ...     },
    ...     "server2": {
    ...         "password": "password2",
    ...     }
    ... }

It will be transformed into::

    >>> {
    ...     "server1": {
    ...         "username": "root",
    ...         "password": "password1",
    ...     },
    ...     "server2": {
    ...         "username": "root",
    ...         "password": "password2",
    ...     },
    ... }

The ``_shared`` key is used to specify the shared values. It is a key value
pair where the key is a path to the value.
"""

import typing as T

SHARED = "_shared"

_error_tpl = (
    "node at JSON path {_prefix!r} is not a dict or list of dict! "
    "cannot set node value '{prefix}.{key}' = ...!"
)


def make_type_error(prefix: str, key: str) -> TypeError:
    if prefix == "":
        _prefix = "."
    else:
        _prefix = prefix
    return TypeError(_error_tpl.format(_prefix=_prefix, prefix=prefix, key=key))


def inherit_shared_value(
    path: str,
    value: T.Any,
    data: T.Union[T.Dict[str, T.Any], T.List[T.Dict[str, T.Any]]],
    _prefix: T.Optional[str] = None,
):
    """
    Try to inherit a shared value to a specific item in a list or dict. If the
    value is already set, then do nothing. It will update the data inplace.

    :param path: JSON path in dot notation to the value to be set.
        Valid path examples: ``key1.key2``, ``databases.*.username``.
        It cannot ends with ``.*``.
    :param value: the value to be set.
    :param data: the data to be updated.
    """
    if path.endswith("*"):
        raise ValueError("json path cannot ends with *!")
    if _prefix is None:
        _prefix = ""

    parts = path.split(".")

    if len(parts) == 1:
        if isinstance(data, dict):
            data.setdefault(parts[0], value)
        elif isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    raise make_type_error(_prefix, parts[0])
                item.setdefault(parts[0], value)
        else:
            raise make_type_error(_prefix, parts[0])
        return

    key = parts[0]
    if key == "*":
        for k, v in data.items():
            if k != SHARED:
                inherit_shared_value(
                    path=".".join(parts[1:]),
                    value=value,
                    data=v,
                    _prefix=f"{_prefix}.{key}",
                )
    else:
        if isinstance(data, dict):
            inherit_shared_value(
                path=".".join(parts[1:]),
                value=value,
                data=data[key],
                _prefix=f"{_prefix}.{key}",
            )
        elif isinstance(data, list):
            for item in data:
                inherit_shared_value(
                    path=".".join(parts[1:]),
                    value=value,
                    data=item[key],
                    _prefix=f"{_prefix}.{key}",
                )
        else:
            raise make_type_error(_prefix, key)


def apply_shared_value(data: dict):
    """
    Transform the data inplace by applying the shared values. It uses
    deep-first search to traverse the data, because deeper node value may
    override the value of the same key in the upper node.
    """
    # implement recursion pattern
    for key, value in data.items():
        if key == SHARED:
            continue
        if isinstance(value, dict):
            apply_shared_value(value)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    apply_shared_value(item)

    # try to set shared value
    has_shared = SHARED in data
    if has_shared is False:
        return

    # pop the shared data, it is not needed in the final result
    shared_data = data.pop(SHARED)
    for path, value in shared_data.items():
        inherit_shared_value(path=path, value=value, data=data)

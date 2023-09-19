# -*- coding: utf-8 -*-

"""
The ``list-aws-resources`` API sometime is very slow, we would like to cache
the result to speed up the search.
"""

import typing as T
from diskcache import Cache
from pathlib_mate import Path

from .paths import dir_cache

dir_cache.parent.mkdir(parents=True, exist_ok=True)


def decohints(decorator: T.Callable) -> T.Callable:
    return decorator


class TypedCache(Cache):
    """
    The original ``diskcache.Cache.memoize`` method will mess up the type hint
    of the decorated function, this class fix this issue.

    Usage::

        cache = TypedCache("/path/to/cache/dir")

        @cache.typed_memoize()
        def very_slow_method() -> T.List[str]:
            pass
    """
    def typed_memoize(self, name=None, typed=False, expire=None, tag=None, ignore=()):
        @decohints
        def decorator(func):
            return self.memoize(name, typed, expire, tag, ignore)(func)

        return decorator


cache = TypedCache(dir_cache.abspath)


def clear_cache():
    Path(cache.directory).remove_if_exists()

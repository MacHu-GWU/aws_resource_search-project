# -*- coding: utf-8 -*-

import typing as T
from diskcache import Cache
from pathlib_mate import Path

from .paths import dir_cache

dir_cache.parent.mkdir(parents=True, exist_ok=True)


def decohints(decorator: T.Callable) -> T.Callable:
    return decorator


class TypedCache(Cache):
    def typed_memoize(self, name=None, typed=False, expire=None, tag=None, ignore=()):
        @decohints
        def decorator(func):
            return self.memoize(name, typed, expire, tag, ignore)(func)

        return decorator


cache = TypedCache(dir_cache.abspath)


def clear_cache():
    Path(cache.directory).remove_if_exists()

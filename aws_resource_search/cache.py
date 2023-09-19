# -*- coding: utf-8 -*-

"""
The ``list-aws-resources`` API sometime is very slow, we would like to cache
the result to speed up the search.
"""

import typing as T
import functools
from diskcache import Cache, ENOVAL
from pathlib_mate import Path

from .paths import dir_cache

if T.TYPE_CHECKING:
    from .res.searcher import Searcher


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


def full_name(func):
    """Return full name of `func` by adding the module and function name."""
    return func.__module__ + "." + func.__qualname__


def args_to_key(base, args, kwargs):
    """
    Create cache key out of function arguments.

    :param tuple base: base of key
    :param tuple args: function arguments
    :param dict kwargs: function keyword arguments
    :return: cache key tuple
    """
    sr: "Searcher" = args[0]
    args = (
        sr.aws_access_key_id,
        sr.aws_secret_access_key,
        sr.aws_session_token,
        sr.region_name,
        sr.profile_name,
    ) + args[1:]
    key = base + args + (None,)

    if kwargs:
        kwargs = dict(kwargs)
        sorted_items = sorted(kwargs.items())

        for item in sorted_items:
            key += item

    return key


class SearchCache(Cache):
    def _better_memoize(
        self,
        expire: T.Optional[int] = None,
        tag: T.Optional[str] = None,
    ):
        def decorator(func):
            """Decorator created by memoize() for callable `func`."""
            base = (full_name(func),)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                """Wrapper for callable to cache arguments and return values."""
                key = wrapper.__cache_key__(*args, **kwargs)

                result = self.get(key, default=ENOVAL, retry=True)

                if result is ENOVAL:
                    result = func(*args, **kwargs)
                    if expire is None or expire > 0:
                        self.set(key, result, expire, tag=tag, retry=True)

                return result

            def __cache_key__(*args, **kwargs):
                """Make key for cache given function arguments."""
                return args_to_key(base, args, kwargs)

            wrapper.__cache_key__ = __cache_key__
            return wrapper

        return decorator

    def better_memoize(
        self,
        expire: T.Optional[int] = None,
        tag: T.Optional[str] = None,
    ):
        @decohints
        def decorator(func):
            return self._better_memoize(expire, tag)(func)

        return decorator


cache = SearchCache(dir_cache.abspath)


def clear_cache():
    Path(cache.directory).remove_if_exists()

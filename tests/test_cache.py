# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from diskcache import Cache
from aws_resource_search.cache import (
    dir_cache,
    TypedCache,
)


class MyClass:
    def my_method(self):
        pass


cache = Cache(dir_cache.abspath)
typed_cache = TypedCache(dir_cache.abspath)


@cache.memoize()
def get1() -> MyClass:
    return MyClass()


@typed_cache.typed_memoize()
def get2() -> MyClass:
    return MyClass()


class TestTypedCache:
    def test(self):
        my_class = get1()
        my_class.my_method()
        my_class = get2()
        my_class.my_method()


if __name__ == "__main__":
    from aws_resource_search.tests import run_cov_test

    run_cov_test(__file__, "aws_resource_search.cache", preview=False)

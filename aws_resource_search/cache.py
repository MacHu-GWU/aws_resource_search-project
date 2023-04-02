# -*- coding: utf-8 -*-

from diskcache import Cache
from pathlib_mate import Path

from .paths import dir_cache

dir_cache.parent.mkdir(parents=True, exist_ok=True)
cache = Cache(dir_cache.abspath)


def clear_cache():
    Path(cache.directory).remove_if_exists()

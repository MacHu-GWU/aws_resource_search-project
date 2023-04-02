# -*- coding: utf-8 -*-

from diskcache import Cache

from .paths import dir_cache

dir_cache.parent.mkdir(parents=True, exist_ok=True)
cache = Cache(dir_cache.abspath)

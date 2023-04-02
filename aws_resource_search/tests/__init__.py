# -*- coding: utf-8 -*-

from .helper import run_cov_test
from .. import paths

paths.dir_cache = paths.dir_tests.joinpath("tmp", "cache")

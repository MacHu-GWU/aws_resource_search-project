# -*- coding: utf-8 -*-

import typing as T
import shutil
import importlib
import dataclasses
from pathlib import Path

from diskcache import Cache
import aws_console_url.api as aws_console_url

from .compat import cached_property
from .paths import dir_index, dir_cache
from .searchers import lookup
from .res_lib import Searcher

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager


def get_searcher_by_resource_type(resource_type: str) -> Searcher:
    mod = lookup[resource_type]["mod"]
    var = lookup[resource_type]["var"]
    module = importlib.import_module(f"aws_resource_search.res.{mod}")
    searcher = getattr(module, var)
    return searcher


@dataclasses.dataclass
class ARSBase:
    bsm: "BotoSesManager" = dataclasses.field()
    dir_index: Path = dataclasses.field(default=dir_index)
    dir_cache: Path = dataclasses.field(default=dir_cache)
    cache: Cache = dataclasses.field(default=None)

    def __post_init__(self):
        self.dir_index = Path(self.dir_index)
        if self.dir_cache is not None:  # pragma: no cover
            self.dir_cache = Path(self.dir_cache)
        if self.cache is None:
            self.cache = Cache(str(self.dir_cache), disk_pickle_protocol=5)
        else:  # pragma: no cover
            self.dir_cache = Path(self.cache.directory)

    @cached_property
    def aws_console(self) -> aws_console_url.AWSConsole:
        return aws_console_url.AWSConsole(
            aws_account_id=self.bsm.aws_account_id,
            aws_region=self.bsm.aws_region,
            bsm=self.bsm,
        )

    def _get_searcher(self, resource_type: str) -> Searcher:
        sr = get_searcher_by_resource_type(resource_type)
        sr.bsm = self.bsm
        return sr

    def clear_all_cache(self):
        shutil.rmtree(self.dir_index, ignore_errors=True)
        shutil.rmtree(self.dir_cache, ignore_errors=True)

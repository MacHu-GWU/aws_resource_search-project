# -*- coding: utf-8 -*-

"""
Todo: doc string here
"""

import typing as T
import shutil
import dataclasses
from pathlib import Path

from diskcache import Cache

from .paths import dir_index, dir_cache
from .searcher_finder import SearcherFinder, searcher_finder

if T.TYPE_CHECKING:
    import aws_console_url.api as aws_console_url
    from boto_session_manager import BotoSesManager
    from .res_lib_v1 import T_SEARCHER


@dataclasses.dataclass
class ARSBase:
    """
    This class is a singleton object that holds all context data such as
    ``boto_session_manager.BotoSesManager``, ``aws_console_url.api.AwsConsole``.

    If you use ``aws_resource_search`` as a Python library (not CLI),
    This is the first object you should import.
    """

    bsm: "BotoSesManager" = dataclasses.field()
    aws_console: "aws_console_url.AWSConsole" = dataclasses.field()
    searcher_finder: "SearcherFinder" = dataclasses.field(default=searcher_finder)
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

    def get_searcher(self, resource_type: str) -> "T_SEARCHER":
        """
        Get corresponding :class:`aws_resource_search.res_lib.Searcher`
        object by resource type.
        """
        sr = searcher_finder.import_searcher(resource_type)
        sr.bsm = self.bsm
        return sr

    def clear_all_cache(self):
        """
        Clear all cache.
        """
        shutil.rmtree(self.dir_index, ignore_errors=True)
        shutil.rmtree(self.dir_cache, ignore_errors=True)

    def all_resource_types(self) -> T.List[str]:
        """
        Return all resource types.
        """
        return searcher_finder.all_resource_types()

    def is_valid_resource_type(self, resource_type: str) -> bool:
        """
        Check if the resource type is supported.
        """
        return searcher_finder.is_valid_resource_type(resource_type)

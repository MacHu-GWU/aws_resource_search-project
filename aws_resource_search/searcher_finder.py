# -*- coding: utf-8 -*-

"""
All AWS resource searchers are defined as variables in the
``aws_resource_search.res.${service}.py`` module. We don't want to import them
manually in the code; instead, we need a lazy-loading mechanism to import them
programmatically based on the resource type.
"""

import typing as T
import json
import importlib
import dataclasses

from .paths import path_searchers_json
from .searcher_metadata import SearcherMetadata

if T.TYPE_CHECKING:  # pragma: no cover
    from .base_searcher import T_SEARCHER


@dataclasses.dataclass
class SearcherFinder:
    """
    This is a helper class to access the implemented searcher metadata,
    and also import the per-aws-resource-type searcher object.
    """

    sm_meta_mapper: T.Dict[str, SearcherMetadata] = dataclasses.field(init=False)
    searcher_cache: T.Dict[str, "T_SEARCHER"] = dataclasses.field(default_factory=dict)

    def reload(self):
        """
        Reload the lookup data from ``aws_resource_search/searchers.json``.
        """
        data = json.loads(path_searchers_json.read_text())
        self.sm_meta_mapper = {
            id: SearcherMetadata(
                id=id,
                desc=dct["desc"],
                ngram=dct["ngram"],
                module=dct["module"],
                var=dct["var"],
            )
            for id, dct in data.items()
        }

    def __post_init__(self):
        self.reload()

    def all_resource_types(self) -> T.List[str]:
        """
        Return all resource types.
        """
        return list(self.sm_meta_mapper.keys())

    def is_valid_resource_type(self, resource_type: str) -> bool:
        """
        Check if the resource type is supported.
        """
        return resource_type in self.sm_meta_mapper

    def import_searcher(self, resource_type: str) -> "T_SEARCHER":
        """
        Import the searcher object by resource type, it uses cache to avoid
        loading the same module multiple times.
        """
        if self.is_valid_resource_type(resource_type):
            if resource_type not in self.searcher_cache:
                mod = searcher_finder.sm_meta_mapper[resource_type].module
                var = searcher_finder.sm_meta_mapper[resource_type].var
                module = importlib.import_module(f"aws_resource_search.res.{mod}")
                self.searcher_cache[resource_type] = getattr(module, var)
            return self.searcher_cache[resource_type]
        else:
            raise ValueError(f"Invalid resource type: {resource_type}")


searcher_finder = SearcherFinder()  # singleton object

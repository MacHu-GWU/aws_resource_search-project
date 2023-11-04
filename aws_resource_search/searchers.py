# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses

from .model import SearcherMetadata
from .paths import path_searchers_json


@dataclasses.dataclass
class SearcherFinder:
    """
    This is a helper class to access the implemented searcher metadata.
    """

    sm_meta_mapper: T.Dict[str, SearcherMetadata] = dataclasses.field(init=False)

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


finder = SearcherFinder()  # singleton object

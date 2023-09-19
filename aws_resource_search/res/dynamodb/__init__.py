# -*- coding: utf-8 -*-

"""
todo: docstring
"""

import typing as T
import dataclasses

from ...model import BaseModel
from ...cache import cache
from ...constants import LIST_API_CACHE_EXPIRE, FILTER_API_CACHE_EXPIRE
from ...fuzzy import FuzzyMatcher
from ..searcher import Searcher


@dataclasses.dataclass
class Table(BaseModel):
    name: T.Optional[str] = dataclasses.field(default=None)


class TableFuzzyMatcher(FuzzyMatcher[Table]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class DynamoDBSearcher(Searcher):
    """
    todo: docstring
    """

    def parse_list_tables(self, res) -> T.List[Table]:
        return [
            Table(
                name=table_name,
            )
            for table_name in res["TableNames"]
        ]

    @cache.better_memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_tables(
        self,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[Table]:
        paginator = self.bsm.dynamodb_client.get_paginator("list_tables")
        tables = list()
        for res in paginator.paginate(
            PaginationConfig=dict(
                MaxItems=max_items,
                PageSize=page_size,
            ),
        ):
            tables.extend(self.parse_list_tables(res))
        return tables

    @cache.better_memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_tables(self, query_str: str) -> T.List[Table]:
        return TableFuzzyMatcher.from_items(self.list_tables()).match(query_str)

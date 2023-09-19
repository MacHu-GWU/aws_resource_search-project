# -*- coding: utf-8 -*-

"""
todo: docstring
"""

import typing as T
import dataclasses

from ...model import BaseAwsResourceModel
from ...cache import cache
from ...constants import LIST_API_CACHE_EXPIRE, FILTER_API_CACHE_EXPIRE
from ...fuzzy import FuzzyMatcher
from ..searcher import Searcher


@dataclasses.dataclass
class Table(BaseAwsResourceModel):
    name: T.Optional[str] = dataclasses.field(default=None)
    arn: T.Optional[str] = dataclasses.field(default=None)


class TableFuzzyMatcher(FuzzyMatcher[Table]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class DynamoDBSearcher(Searcher):
    """
    todo: docstring
    """

    def parse_list_tables(self, res) -> T.List[Table]:
        """
        Parse response of: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/list_tables.html
        """
        lst = list()
        for table_name in res.get("TableNames", []):
            table = Table(
                name=table_name,
            )
            self._enrich_aws_account_and_region(table)
            table.arn = self.aws_console.dynamodb.get_table_arn(table.name)
            table.console_url = self.aws_console.dynamodb.get_table_overview(table.name)
            lst.append(table)
        return lst

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

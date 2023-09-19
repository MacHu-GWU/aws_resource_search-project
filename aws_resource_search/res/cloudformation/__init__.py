# -*- coding: utf-8 -*-

"""
todo: docstring
"""

import typing as T
import dataclasses
from datetime import datetime

from ...model import BaseModel
from ...cache import cache
from ...constants import LIST_API_CACHE_EXPIRE, FILTER_API_CACHE_EXPIRE
from ...fuzzy import FuzzyMatcher
from ..searcher import Searcher


@dataclasses.dataclass
class Stack(BaseModel):
    id: T.Optional[str] = dataclasses.field(default=None)
    name: T.Optional[str] = dataclasses.field(default=None)
    create_time: T.Optional[datetime] = dataclasses.field(default=None)
    update_time: T.Optional[datetime] = dataclasses.field(default=None)
    delete_time: T.Optional[datetime] = dataclasses.field(default=None)
    status: T.Optional[str] = dataclasses.field(default=None)
    parent_id: T.Optional[str] = dataclasses.field(default=None)
    root_id: T.Optional[str] = dataclasses.field(default=None)

    @property
    def arn(self) -> str:  # pragma: no cover
        return self.id


class StackFuzzyMatcher(FuzzyMatcher[Stack]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class StackSet(BaseModel):
    id: T.Optional[str] = dataclasses.field(default=None)
    name: T.Optional[str] = dataclasses.field(default=None)
    status: T.Optional[str] = dataclasses.field(default=None)

    def get_arn(self, aws_account_id: str, aws_region: str) -> str:  # pragma: no cover
        return (
            f"arn:aws:cloudformation:{aws_region}:{aws_account_id}:stackset/{self.id}"
        )


class StackSetFuzzyMatcher(FuzzyMatcher[StackSet]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class CloudFormationSearcher(Searcher):
    """
    todo: docstring
    """

    def parse_describe_stacks(self, res) -> T.List[Stack]:
        """
        Parse response of https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stacks.html
        """
        return [
            Stack(
                id=dct.get("StackId"),
                name=dct.get("StackName"),
                create_time=dct.get("CreationTime"),
                update_time=dct.get("LastUpdatedTime"),
                delete_time=dct.get("DeletionTime"),
                status=dct.get("StackStatus"),
                parent_id=dct.get("ParentId"),
                root_id=dct.get("RootId"),
            )
            for dct in res.get("Stacks", [])
        ]

    @cache.better_memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_stacks(
        self,
        max_items: int = 1000,
    ) -> T.List[Stack]:
        paginator = self.bsm.cloudformation_client.get_paginator("describe_stacks")
        stacks = list()
        for res in paginator.paginate(
            PaginationConfig=dict(
                MaxItems=max_items,
            ),
        ):
            stacks.extend(self.parse_describe_stacks(res))
        return stacks

    @cache.better_memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_stacks(self, query_str: str) -> T.List[Stack]:
        return StackFuzzyMatcher.from_items(self.list_stacks()).match(query_str)

    def parse_list_stack_sets(self, res) -> T.List[StackSet]:
        """
        Parse response of https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/list_stack_sets.html
        """
        return [
            StackSet(
                id=dct.get("StackSetId"),
                name=dct.get("StackSetName"),
                status=dct.get("Status"),
            )
            for dct in res.get("Summaries", [])
        ]

    @cache.better_memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_stack_sets(
        self,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[StackSet]:
        paginator = self.bsm.cloudformation_client.get_paginator("list_stack_sets")
        stack_sets = list()
        for res in paginator.paginate(
            PaginationConfig=dict(
                MaxItems=max_items,
                PageSize=page_size,
            ),
        ):
            stack_sets.extend(self.parse_list_stack_sets(res))
        return stack_sets

    @cache.better_memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_stack_sets(self, query_str: str) -> T.List[StackSet]:
        return StackSetFuzzyMatcher.from_items(self.list_stack_sets()).match(query_str)

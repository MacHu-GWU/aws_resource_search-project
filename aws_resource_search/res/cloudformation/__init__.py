# -*- coding: utf-8 -*-

"""
todo: docstring
"""

import typing as T
import dataclasses
from datetime import datetime

from ...model import BaseAwsResourceModel
from ...cache import cache
from ...constants import LIST_API_CACHE_EXPIRE, FILTER_API_CACHE_EXPIRE
from ...fuzzy import FuzzyMatcher
from ..searcher import Searcher


@dataclasses.dataclass
class Stack(BaseAwsResourceModel):
    id: T.Optional[str] = dataclasses.field(default=None)
    name: T.Optional[str] = dataclasses.field(default=None)
    create_time: T.Optional[datetime] = dataclasses.field(default=None)
    update_time: T.Optional[datetime] = dataclasses.field(default=None)
    delete_time: T.Optional[datetime] = dataclasses.field(default=None)
    status: T.Optional[str] = dataclasses.field(default=None)
    parent_id: T.Optional[str] = dataclasses.field(default=None)
    root_id: T.Optional[str] = dataclasses.field(default=None)


class StackFuzzyMatcher(FuzzyMatcher[Stack]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class StackSet(BaseAwsResourceModel):
    id: T.Optional[str] = dataclasses.field(default=None)
    name: T.Optional[str] = dataclasses.field(default=None)
    status: T.Optional[str] = dataclasses.field(default=None)
    permission_model: T.Optional[str] = dataclasses.field(default=None)
    drift_status: T.Optional[str] = dataclasses.field(default=None)

    def is_self_managed(self) -> bool:
        if self.permission_model is None:  # pragma: no cover
            raise ValueError("permission_model is None")
        return self.permission_model == "SELF_MANAGED"

    def is_service_managed(self) -> bool:
        if self.permission_model is None:  # pragma: no cover
            raise ValueError("permission_model is None")
        return self.permission_model == "SERVICE_MANAGED"


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
        lst = list()
        for dct in res.get("Stacks", []):
            stack_arn = dct.get("StackId")
            stack = Stack(
                id=stack_arn,
                name=dct.get("StackName"),
                create_time=dct.get("CreationTime"),
                update_time=dct.get("LastUpdatedTime"),
                delete_time=dct.get("DeletionTime"),
                status=dct.get("StackStatus"),
                parent_id=dct.get("ParentId"),
                root_id=dct.get("RootId"),
                arn=stack_arn,
                console_url=self.aws_console.cloudformation.get_stack(stack_arn),
            )
            self._enrich_aws_account_and_region(stack)
            lst.append(stack)
        return lst

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
        lst = list()
        for dct in res.get("Summaries", []):
            stack_set = StackSet(
                id=dct.get("StackSetId"),
                name=dct.get("StackSetName"),
                status=dct.get("Status"),
                permission_model=dct.get("PermissionModel"),
                drift_status=dct.get("DriftStatus"),
            )
            self._enrich_aws_account_and_region(stack_set)
            if stack_set.permission_model is None:
                stack_set.permission_model = "SELF_MANAGED"
            stack_set.arn = self.aws_console.cloudformation.get_stack_set_arn(
                name=stack_set.name,
                is_self_managed=stack_set.is_self_managed(),
                is_service_managed=stack_set.is_service_managed(),
            )
            stack_set.console_url = self.aws_console.cloudformation.get_stack_set_info(
                name_or_id_or_arn=stack_set.id,
                is_self_managed=stack_set.is_self_managed(),
                is_service_managed=stack_set.is_service_managed(),
            )
            lst.append(stack_set)
        return lst

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

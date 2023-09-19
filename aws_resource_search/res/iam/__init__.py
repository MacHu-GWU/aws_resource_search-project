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
class Role(BaseModel):
    id: T.Optional[str] = dataclasses.field(default=None)
    name: T.Optional[str] = dataclasses.field(default=None)
    description: T.Optional[str] = dataclasses.field(default=None)
    create_date: T.Optional[str] = dataclasses.field(default=None)
    path: T.Optional[str] = dataclasses.field(default=None)
    arn: T.Optional[str] = dataclasses.field(default=None)


class RoleFuzzyMatcher(FuzzyMatcher[Role]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class Policy(BaseModel):
    id: T.Optional[str] = dataclasses.field(default=None)
    name: T.Optional[str] = dataclasses.field(default=None)
    description: T.Optional[str] = dataclasses.field(default=None)
    update_date: T.Optional[str] = dataclasses.field(default=None)
    path: T.Optional[str] = dataclasses.field(default=None)
    arn: T.Optional[str] = dataclasses.field(default=None)


class PolicyFuzzyMatcher(FuzzyMatcher[Policy]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class User(BaseModel):
    id: T.Optional[str] = dataclasses.field(default=None)
    name: T.Optional[str] = dataclasses.field(default=None)
    create_date: T.Optional[str] = dataclasses.field(default=None)
    path: T.Optional[str] = dataclasses.field(default=None)
    arn: T.Optional[str] = dataclasses.field(default=None)


class UserFuzzyMatcher(FuzzyMatcher[User]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class IamSearcher(Searcher):
    """
    Reference:

    - IAM object quotas: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html#reference_iam-quotas-entities
    """

    def parse_list_roles(self, res) -> T.List[Role]:
        return [
            Role(
                id=role_dict["RoleId"],
                name=role_dict["RoleName"],
                description=role_dict.get("Description"),
                create_date=str(role_dict["CreateDate"]),
                path=role_dict["Path"],
                arn=role_dict["Arn"],
            )
            for role_dict in res["Roles"]
        ]

    @cache.better_memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_roles(
        self,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[Role]:
        paginator = self.bsm.iam_client.get_paginator("list_roles")
        roles = list()
        for res in paginator.paginate(
            PaginationConfig=dict(
                MaxItems=max_items,
                PageSize=page_size,
            )
        ):
            roles.extend(self.parse_list_roles(res))
        return roles

    @cache.better_memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_roles(
        self,
        query_str: str,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[Role]:
        return RoleFuzzyMatcher.from_items(
            self.list_roles(
                max_items=max_items,
                page_size=page_size,
            )
        ).match(query_str)

    def parse_list_policies(self, res) -> T.List[Policy]:
        return [
            Policy(
                id=policy_dict["PolicyId"],
                name=policy_dict["PolicyName"],
                description=policy_dict.get("Description"),
                update_date=str(policy_dict["UpdateDate"]),
                path=policy_dict["Path"],
                arn=policy_dict["Arn"],
            )
            for policy_dict in res["Policies"]
        ]

    @cache.better_memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_policies(
        self,
        scope_is_all: bool = False,
        scope_is_aws: bool = False,
        scope_is_local: bool = False,
        only_attached: bool = False,
        path_prefix: T.Optional[str] = None,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[Policy]:
        flag_count = sum(
            [
                scope_is_all,
                scope_is_aws,
                scope_is_local,
            ]
        )
        if flag_count != 1:
            raise ValueError(
                "one of scope_is_all, scope_is_aws, scope_is_local must be set to True"
            )
        if scope_is_all:  # pragma: no cover
            Scope = "All"
        elif scope_is_aws:  # pragma: no cover
            Scope = "AWS"
        elif scope_is_local:
            Scope = "Local"
        else:  # pragma: no cover
            raise NotImplementedError

        kwargs = dict(
            Scope=Scope,
            OnlyAttached=only_attached,
            MaxItems=5000,
            PaginationConfig=dict(
                MaxItems=max_items,
                PageSize=page_size,
            ),
        )
        if path_prefix is not None:  # pragma: no cover
            kwargs["PathPrefix"] = path_prefix

        paginator = self.bsm.iam_client.get_paginator("list_policies")
        policies = list()
        for res in paginator.paginate(**kwargs):
            policies.extend(self.parse_list_policies(res))
        return policies

    @cache.better_memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_policies(
        self,
        query_str: str,
        scope_is_all: bool = False,
        scope_is_aws: bool = False,
        scope_is_local: bool = False,
        only_attached: bool = False,
        path_prefix: T.Optional[str] = None,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[Policy]:
        return PolicyFuzzyMatcher.from_items(
            self.list_policies(
                scope_is_all=scope_is_all,
                scope_is_aws=scope_is_aws,
                scope_is_local=scope_is_local,
                only_attached=only_attached,
                path_prefix=path_prefix,
                max_items=max_items,
                page_size=page_size,
            )
        ).match(query_str)

    def parse_list_users(self, res) -> T.List[User]:
        return [
            User(
                id=user_dict["UserId"],
                name=user_dict["UserName"],
                create_date=str(user_dict["CreateDate"]),
                path=user_dict["Path"],
                arn=user_dict["Arn"],
            )
            for user_dict in res["Users"]
        ]

    @cache.better_memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_users(
        self,
        path_prefix: T.Optional[str] = None,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[User]:
        paginator = self.bsm.iam_client.get_paginator("list_users")
        users = list()
        kwargs = dict(
            MaxItems=5000,
            PaginationConfig=dict(
                MaxItems=max_items,
                PageSize=page_size,
            ),
        )
        if path_prefix is not None:
            kwargs["PathPrefix"] = path_prefix
        for res in paginator.paginate(**kwargs):
            users.extend(self.parse_list_users(res))
        return users

    @cache.better_memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_users(
        self,
        query_str: str,
        path_prefix: T.Optional[str] = None,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[User]:
        return UserFuzzyMatcher.from_items(
            self.list_users(
                path_prefix=path_prefix,
                max_items=max_items,
                page_size=page_size,
            )
        ).match(query_str)

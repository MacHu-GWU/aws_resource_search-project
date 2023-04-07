# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from ...model import BaseModel
from ...cache import cache
from ...boto_ses import aws
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
class IamSearcher(Searcher):
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

    @cache.memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_roles(self) -> T.List[Role]:
        paginator = aws.bsm.iam_client.get_paginator("list_roles")
        roles = list()
        for res in paginator.paginate():
            roles.extend(self.parse_list_roles(res))
        return roles


    @cache.memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_roles(self, query_str: str) -> T.List[Role]:
        return RoleFuzzyMatcher.from_items(
            self.list_roles()
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

    @cache.memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_policies(
        self,
        scope_is_all: bool = False,
        scope_is_aws: bool = False,
        scope_is_local: bool = False,
        only_attached: bool = False,
        path_prefix: T.Optional[str] = None,
    ) -> T.List[Policy]:
        flag_count = sum([
            scope_is_all,
            scope_is_aws,
            scope_is_local,
        ])
        if flag_count != 1:
            raise ValueError("one of scope_is_all, scope_is_aws, scope_is_local must be set to True")
        if scope_is_all:
            Scope = "All"
        elif scope_is_aws:
            Scope = "AWS"
        elif scope_is_local:
            Scope = "Local"
        else: # pragma: no cover
            raise NotImplementedError

        kwargs = dict(
            Scope=Scope,
            OnlyAttached=only_attached,
        )
        if path_prefix is not None:
            kwargs["PathPrefix"] = path_prefix

        paginator = aws.bsm.iam_client.get_paginator("list_policies")
        policies = list()
        for res in paginator.paginate(**kwargs):
            policies.extend(self.parse_list_policies(res))
        return policies

    @cache.memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_policies(
        self,
        query_str: str,
        scope_is_all: bool = False,
        scope_is_aws: bool = False,
        scope_is_local: bool = False,
        only_attached: bool = False,
        path_prefix: T.Optional[str] = None,
    ) -> T.List[Policy]:
        return PolicyFuzzyMatcher.from_items(
            self.list_policies(
                scope_is_all=scope_is_all,
                scope_is_aws=scope_is_aws,
                scope_is_local=scope_is_local,
                only_attached=only_attached,
                path_prefix=path_prefix,
            )
        ).match(query_str)
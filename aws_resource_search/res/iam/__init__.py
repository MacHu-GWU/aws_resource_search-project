# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from ...model import BaseModel
from ...cache import cache
from ...boto_ses import aws
from ...constants import CACHE_EXPIRE
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
class IamSearcher(Searcher):
    def parse_response(self, res) -> T.List[Role]:
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

    @cache.memoize(expire=CACHE_EXPIRE)
    def list_roles(self) -> T.List[Role]:
        paginator = aws.bsm.iam_client.get_paginator("list_roles")
        roles = list()
        for res in paginator.paginate():
            roles.extend(self.parse_response(res))
        return roles


    @cache.memoize(expire=CACHE_EXPIRE)
    def filter_roles(self, query_str: str) -> T.List[Role]:
        return RoleFuzzyMatcher.from_items(
            self.list_roles()
        ).match(query_str)

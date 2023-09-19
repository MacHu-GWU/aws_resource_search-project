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
class Bucket(BaseModel):
    """
    todo: docstring
    """
    name: T.Optional[str] = dataclasses.field(default=None)
    create_date: T.Optional[str] = dataclasses.field(default=None)

    @property
    def arn(self):
        return "arn:aws:s3:::{}".format(self.name)


class BucketFuzzyMatcher(FuzzyMatcher[Bucket]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class S3Searcher(Searcher):
    """
    Reference:
    """

    def parse_list_buckets(self, res) -> T.List[Bucket]:
        return [
            Bucket(
                name=bucket_dict["Name"],
                create_date=str(bucket_dict["CreationDate"]),
            )
            for bucket_dict in res["Buckets"]
        ]

    @cache.better_memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_buckets(self) -> T.List[Bucket]:
        """
        s3 list_buckets doesn't have paginator.
        """
        return self.parse_list_buckets(self.bsm.s3_client.list_buckets())

    @cache.better_memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_buckets(self, query_str: str) -> T.List[Bucket]:
        return BucketFuzzyMatcher.from_items(self.list_buckets()).match(query_str)

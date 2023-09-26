# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from pathlib import Path

from diskcache import Cache
import sayt.api as sayt
from boto_session_manager import BotoSesManager
import aws_console_url.api as aws_console_url
from fixa.timer import DateTimeTimer

from .compat import cached_property
from .paths import dir_index, dir_cache
from .data.request import Request
from .data.search import Search


@dataclasses.dataclass
class ResourceSearcher:
    """
    :param bsm:
    :param aws_console:
    :param service_id:
    :param resource_type:
    :param request:
    :param search:
    :param dir_index:
    :param dir_cache:
    :param cache_expire: 指定被搜索的数据集的缓存过期时间, 单位秒. 当缓存过期时, 会重新
        调用 boto3 API 获取数据并重新构建索引.
    """

    bsm: BotoSesManager = dataclasses.field()
    aws_console: aws_console_url.AWSConsole = dataclasses.field()
    service_id: str = dataclasses.field()
    resource_type: str = dataclasses.field()
    request: Request = dataclasses.field()
    search: Search = dataclasses.field()
    dir_index: Path = dataclasses.field(default=dir_index)
    dir_cache: Path = dataclasses.field(default=dir_cache)
    cache_expire: int = dataclasses.field(default=3600)

    @cached_property
    def cache(self) -> Cache:
        return Cache(str(self.dir_cache))

    @cached_property
    def index_name(self) -> str:
        return f"{self.bsm.aws_account_id}-{self.bsm.aws_region}-{self.service_id}-{self.resource_type}"

    @cached_property
    def cache_key(self) -> str:
        """
        用于缓存 API Call 的结果的 key. 由你所用的 boto session 的 aws_account_id, aws_region,
        以及你所要搜索的资源的 service_id, resource_type 组成. 这个 key 最终也会被用于
        构成 Query 结果的 cache key.
        """
        return f"{self.bsm.aws_account_id}-{self.bsm.aws_region}-{self.service_id}-{self.resource_type}"

    @cached_property
    def cache_tag(self) -> str:
        """
        这个 Tag 是用于在清除缓存时, 批量清除所有带有这个 Tag 的缓存的. 我们只有在数据集缓存
        过期后, 才需要清理掉所有这个数据集所有的 Query 的缓存. 同样, 这个 Tag 也是由
        aws_account_id, aws_region, service_id, resource_type 组成.
        """
        return f"{self.bsm.aws_account_id}-{self.bsm.aws_region}-{self.service_id}-{self.resource_type}"

    @cached_property
    def sayt_dataset(self) -> sayt.DataSet:
        return sayt.DataSet(
            dir_index=self.dir_index,
            index_name=self.index_name,
            fields=[field._to_sayt_field() for field in self.search.fields],
            cache=self.cache,
            cache_key=self.cache_key,
            cache_tag=self.cache_tag,
            cache_expire=self.cache_expire,
        )

    def _refresh_data(self, boto_kwargs: T.Optional[dict] = None):
        with DateTimeTimer("remove index"):
            self.sayt_dataset.remove_index()
        with DateTimeTimer("remove cache"):
            self.sayt_dataset.remove_cache()
        with DateTimeTimer("call api"):
            items = self.request.invoke(self.bsm, boto_kwargs).all()
        with DateTimeTimer("item to doc"):
            docs = [self.search._item_to_doc(item) for item in items]
        self.cache.set(
            self.cache_key,
            1,
            expire=self.cache_expire,
            tag=self.cache_tag,
        )
        with DateTimeTimer("build index"):
            self.sayt_dataset.build_index(docs, rebuild=False)

    def query(
        self,
        q: str,
        limit: int = 20,
        boto_kwargs: T.Optional[dict] = None,
        refresh_data: bool = False,
    ):
        if refresh_data:
            self._refresh_data(boto_kwargs=boto_kwargs)
        elif self.cache_key not in self.cache:
            self._refresh_data(boto_kwargs=boto_kwargs)
        else:
            pass
        with DateTimeTimer("search"):
            res = self.sayt_dataset.search(q, limit=limit)
        return res

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
from .constants import CONSOLE_URL
from .data.request import Request
from .data.output import Attribute, extract_output
from .data.document import Field, extract_document
from .data.url import Url


def get_boto_session_fingerprint(bsm: "BotoSesManager") -> str:
    """
    Get the logical unique fingerprint of the boto3 session. It is used in
    the index name and cache key.
    """
    sep = "----"
    parts = []
    if bsm.profile_name is None:
        parts.append(bsm.aws_account_id)
        parts.append(bsm.aws_region)
    else:
        parts.append(bsm.profile_name)
        if bsm.aws_region is not None:
            parts.append(bsm.aws_region)
    return sep.join(parts)


@dataclasses.dataclass
class ResourceSearcher:
    """
    :param bsm:
    :param aws_console:
    :param service_id:
    :param resource_type:
    :param request:
    :param output:
    :param document:
    :param url:
    :param dir_index:
    :param dir_cache:
    :param cache:
    :param cache_expire: 指定被搜索的数据集的缓存过期时间, 单位秒. 当缓存过期时, 会重新
        调用 boto3 API 获取数据并重新构建索引.
    """

    bsm: BotoSesManager = dataclasses.field()
    aws_console: aws_console_url.AWSConsole = dataclasses.field()
    service_id: str = dataclasses.field()
    resource_type: str = dataclasses.field()
    request: Request = dataclasses.field()
    output: T.Dict[str, Attribute] = dataclasses.field()
    document: T.Dict[str, Field] = dataclasses.field()
    url: Url = dataclasses.field()
    dir_index: Path = dataclasses.field(default=dir_index)
    dir_cache: Path = dataclasses.field(default=dir_cache)
    cache: Cache = dataclasses.field(default=None)
    cache_expire: int = dataclasses.field(default=3600)

    def __post_init__(self):
        if self.dir_cache is not None:  # pragma: no cover
            self.dir_cache = Path(self.dir_cache)
        if self.cache is None:  # pragma: no cover
            self.cache = Cache(str(self.dir_cache))
        else:
            self.dir_cache = Path(self.cache.directory)

    @cached_property
    def index_name(self) -> str:
        return f"{get_boto_session_fingerprint(self.bsm)}-{self.service_id}-{self.resource_type}"

    @cached_property
    def cache_key(self) -> str:
        """
        用于缓存 API Call 的结果的 key. 由你所用的 boto session 的 fingerprint,
        以及你所要搜索的资源的 service_id, resource_type 组成. 这个 key 最终也会被用于
        构成 Query 结果的 cache key.
        """
        return f"{get_boto_session_fingerprint(self.bsm)}-{self.service_id}-{self.resource_type}"

    @cached_property
    def cache_tag(self) -> str:
        """
        这个 Tag 是用于在清除缓存时, 批量清除所有带有这个 Tag 的缓存的. 我们只有在数据集缓存
        过期后, 才需要清理掉所有这个数据集所有的 Query 的缓存. 同样, 这个 Tag 也是由
        boto session 的 fingerprint, service_id, resource_type 组成.
        """
        return f"{get_boto_session_fingerprint(self.bsm)}-{self.service_id}-{self.resource_type}"

    @cached_property
    def sayt_dataset(self) -> sayt.DataSet:
        return sayt.DataSet(
            dir_index=self.dir_index,
            index_name=self.index_name,
            fields=[field._to_sayt_field() for field in self.document.values()],
            cache=self.cache,
            cache_key=self.cache_key,
            cache_tag=self.cache_tag,
            cache_expire=self.cache_expire,
        )

    @cached_property
    def context(self) -> T.Dict[str, T.Any]:
        return {
            "AWS_ACCOUNT_ID": self.bsm.aws_account_id,
            "AWS_REGION": self.bsm.aws_region,
        }

    def _refresh_data(self, boto_kwargs: T.Optional[dict] = None):
        # with DateTimeTimer("remove index"):
        self.sayt_dataset.remove_index()
        # with DateTimeTimer("remove cache"):
        self.sayt_dataset.remove_cache()
        # with DateTimeTimer("call api"):
        res_list = self.request.send(self.bsm, boto_kwargs)
        # with DateTimeTimer("item to doc"):
        context = self.context
        doc_list = [
            extract_document(
                document=self.document,
                output=extract_output(
                    output=self.output,
                    resource=res,
                    context=context,
                ),
            )
            for res in res_list
        ]
        self.cache.set(
            self.cache_key,
            1,
            expire=self.cache_expire,
            tag=self.cache_tag,
        )
        # with DateTimeTimer("build index"):
        self.sayt_dataset.build_index(doc_list, rebuild=False)

    def query(
        self,
        q: str,
        limit: int = 20,
        boto_kwargs: T.Optional[dict] = None,
        refresh_data: bool = False,
    ):
        if refresh_data:
            # print("force refresh data:")
            self._refresh_data(boto_kwargs=boto_kwargs)
        elif self.cache_key not in self.cache:
            self._refresh_data(boto_kwargs=boto_kwargs)
        else:
            pass
        # with DateTimeTimer("search"):
        docs = self.sayt_dataset.search(q, limit=limit)
        for doc in docs:
            doc[CONSOLE_URL] = self.url.get(document=doc, aws_console=self.aws_console)
        return docs

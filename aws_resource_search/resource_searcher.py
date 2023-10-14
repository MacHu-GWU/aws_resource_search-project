# -*- coding: utf-8 -*-

"""
Low level API for searching AWS resources.
"""

import typing as T
import dataclasses
import contextlib
import shutil
from pathlib import Path

from diskcache import Cache
import sayt.api as sayt
from boto_session_manager import BotoSesManager
import aws_console_url.api as aws_console_url
from fixa.timer import TimeTimer

from .logger import logger
from .compat import cached_property
from .paths import dir_index, dir_cache
from .constants import CONSOLE_URL, SEP
from .utils import get_md5_hash
from .data.types import T_DATA
from .data.request import Request
from .data.output import Attribute, extract_output
from .data.document import Field, extract_document
from .data.url import Url
from .utils import get_md5_hash


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
        调用 boto3 API 获取数据并重新构建索引. 注意, query 缓存应该是永不过期的, 因为你
        数据集不更新, 缓存也没有必要更新, 同样的搜索的结果必然是一样的.
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
        if self.cache is None:
            # diskcache uses pickle to serialize cache key, we have to hard code
            # the protocol value to make it consistent across different python
            self.cache = Cache(str(self.dir_cache), disk_pickle_protocol=5)
        else:  # pragma: no cover
            self.dir_cache = Path(self.cache.directory)

    @cached_property
    def _bsm_fingerprint(self) -> T.Tuple[str, T.Optional[str]]:
        """
        Get the logical unique fingerprint of the boto3 session. It will be
        used in the index name and cache key naming convention.
        """
        if str(self.bsm.profile_name) == "Sentinel('NOTHING')":
            account_or_profile = self.bsm.aws_account_id
        else:  # pragma: no cover
            account_or_profile = self.bsm.profile_name
        if self.bsm.aws_region is None:  # pragma: no cover
            region = "unknown-region"
        else:
            region = self.bsm.aws_region
        return account_or_profile, region

    @cached_property
    def index_name(self) -> str:
        """
        用于存储数据集的 whoosh 索引的名字. 由你所用的 boto session 的 fingerprint,
        以及你所要搜索的资源的 service_id, resource_type 组成. 如果你需要搜索的 AWS 资源的
        boto API 带有额外参数, 那么最终的 index name 是这个属性的值加上额外的参数的指纹.
        """
        account_or_profile, region = self._bsm_fingerprint
        return SEP.join(
            [
                account_or_profile,
                region,
                self.service_id,
                self.resource_type,
            ]
        )

    @cached_property
    def base_query_cache_key(self) -> T.Tuple[str, str, str, str]:
        """
        用于缓存 boto API Call 的结果的 key. 由你所用的 boto session 的 fingerprint,
        以及你所要搜索的资源的 service_id, resource_type 组成. 如果你需要搜索的 AWS 资源的
        boto API 带有额外参数, 那么最终的 cache key 是这个属性的值加上额外的参数.

        而最终用于缓存 Query 的结果的 key 还需要加上 query 时用到的参数.
        """
        account_or_profile, region = self._bsm_fingerprint
        return (account_or_profile, region, self.service_id, self.resource_type)

    @cached_property
    def base_query_cache_tag(self) -> str:
        """
        这个 Tag 是用于在清除缓存时, 批量清除所有带有这个 Tag 的缓存的. 我们只有在数据集缓存
        过期后, 才需要清理掉所有这个数据集所有的 Query 的缓存. 同样, 这个 Tag 也是由
        boto session 的 fingerprint, service_id, resource_type 组成.
        """
        return self.index_name

    @cached_property
    def data_cache_tag(self) -> str:
        """
        这个 Tag 是用于在清除属于同一个 boto session 下的所有的 AWS 资源的缓存时, 批量清除
        所有带有这个 Tag 的缓存的.
        """
        return SEP.join(self._bsm_fingerprint)

    def clear_all_cache(self):  # pragma: no cover
        """
        彻底删除所有 index 以及 cache, 直接清空 index 和 cache 的目录.
        """
        shutil.rmtree(self.dir_index, ignore_errors=True)
        shutil.rmtree(self.dir_cache, ignore_errors=True)
        self.cache = Cache(str(self.dir_cache), disk_pickle_protocol=5)

    def clear_aws_account_and_region_cache(self):
        path: Path
        account_or_profile, region = self._bsm_fingerprint
        prefix = f"{get_md5_hash(account_or_profile)[:6]}-{get_md5_hash(region)[:6]}"
        prefix1 = f"_{prefix}"
        for path in self.dir_index.glob("**/*"):
            if path.is_file():
                name = path.name
                if name.startswith(prefix) or name.startswith(prefix1):
                    path.unlink()

        key_to_delete = list()
        account_and_region = f"{account_or_profile}-{region}"
        for key in self.cache.iterkeys():
            value, tag = self.cache.get(key, tag=True)
            if tag.startswith(account_and_region):
                key_to_delete.append(key)
        for key in key_to_delete:
            self.cache.delete(key)

    @cached_property
    def sayt_refreshable_dataset(self) -> sayt.RefreshableDataSet:
        def downloader(
            boto_kwargs: T.Optional[dict] = None,
        ) -> T.List[T.Dict[str, T.Any]]:
            final_boto_kwargs = self.request._merge_boto_kwargs(
                boto_kwargs,
                self.context,
            )
            with TimeTimer(display=False) as timer:
                res_list = self.request.send(
                    self.bsm,
                    _boto_kwargs=final_boto_kwargs,
                ).all()
            # print(res_list[:3])
            logger.info(f"pull data, elapsed: {timer.elapsed:.3f}s")
            logger.info(f"got {len(res_list)} records")
            return res_list

        def cache_key_def(
            download_kwargs: sayt.T_KWARGS,
            context: sayt.T_CONTEXT,
        ):
            final_boto_kwargs = self.request._merge_boto_kwargs(
                download_kwargs["boto_kwargs"],
                self.context,
            )
            if self.request.cache_key:
                more_cache_keys: T.List[str] = self.request._get_additional_cache_key(
                    final_boto_kwargs
                )
                return [*self.base_query_cache_key, *more_cache_keys]
            else:
                return list(self.base_query_cache_key)

        # extractor is a function that converts the record into whoosh document
        def extractor(
            record: sayt.T_RECORD,
            download_kwargs: sayt.T_KWARGS,
            context: sayt.T_CONTEXT,
        ) -> sayt.T_RECORD:
            return extract_document(
                document=self.document,
                output=extract_output(
                    output=self.output,
                    resource=record,
                    context=context,
                ),
            )

        return sayt.RefreshableDataSet(
            downloader=downloader,
            cache_key_def=cache_key_def,
            extractor=extractor,
            fields=[field._to_sayt_field() for field in self.document.values()],
            dir_index=self.dir_index,
            dir_cache=self.dir_cache,
            cache=self.cache,
            cache_expire=self.cache_expire,
        )

    @cached_property
    def context(self) -> T.Dict[str, T.Any]:
        """
        在从 boto API 的结果中进一步提取数据, 丰富数据的时候所需的 context. 同时也会用于
        evaluate boto kwargs 中的 token 时所需的 context.
        """
        return {
            "AWS_ACCOUNT_ID": self.bsm.aws_account_id,
            "AWS_REGION": self.bsm.aws_region,
        }

    @staticmethod
    def _simplify_result(result: sayt.T_Result) -> T.List[dict]:  # pragma: no cover
        return [hit["_source"] for hit in result["hits"]]

    def search(
        self,
        q: str,
        limit: int = 20,
        boto_kwargs: T.Optional[dict] = None,
        refresh_data: bool = False,
        simple_response: bool = False,
        ignore_cache: bool = False,
        verbose: bool = False,
    ) -> T.Union[sayt.T_Result, T.List[dict]]:
        """
        The main public API for AWS Resource Search.

        :param q:
        :param limit:
        :param boto_kwargs:
        :param refresh_data:
        :param simple_response:
        :param ignore_cache:
        :param verbose:
        """
        with logger.disabled(disable=not verbose):
            logger.ruler("start")
            result = self.sayt_refreshable_dataset.search(
                query=q,
                download_kwargs={"boto_kwargs": boto_kwargs},
                refresh_data=refresh_data,
                limit=limit,
                simple_response=False,
                ignore_cache=ignore_cache,
            )
            for hit in result["hits"]:
                url = self.url.get(
                    document=hit["_source"], aws_console=self.aws_console
                )
                hit["_source"][CONSOLE_URL] = url
            elapsed = result["took"] / 1000
            with logger.indent():
                logger.info(f"search time, elapsed: {elapsed:.3f}s")
                logger.info(f"hit {result['size']} docs.")
                logger.info(f"hit cache: {result['cache']}.")
                if result["size"]:
                    logger.info(f"first doc: {result['hits'][0]['_source']}")
            if simple_response:  # pragma: no cover
                result = self._simplify_result(result)
            logger.ruler("end")
        return result

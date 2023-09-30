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
from sayt.dataset import Result
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
    def base_query_cache_key(self) -> str:
        """
        用于缓存 boto API Call 的结果的 key. 由你所用的 boto session 的 fingerprint,
        以及你所要搜索的资源的 service_id, resource_type 组成. 如果你需要搜索的 AWS 资源的
        boto API 带有额外参数, 那么最终的 cache key 是这个属性的值加上额外的参数.

        而最终用于缓存 Query 的结果的 key 还需要加上 query 时用到的参数.
        """
        return self.index_name

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

    def clear_aws_account_and_region_cache(self):
        path: Path
        prefix = SEP.join(self._bsm_fingerprint)
        prefix1 = f"_{prefix}"
        for path in self.dir_index.glob("**/*"):
            if path.is_file():
                name = path.name
                if name.startswith(prefix) or name.startswith(prefix1):
                    path.unlink()
        self.cache.evict(tag=self.data_cache_tag)

    @cached_property
    def sayt_dataset(self) -> sayt.DataSet:
        return sayt.DataSet(
            dir_index=self.dir_index,
            index_name=self.index_name,
            fields=[field._to_sayt_field() for field in self.document.values()],
            cache=self.cache,
            cache_key=self.base_query_cache_key,
            cache_tag=self.base_query_cache_tag,
            cache_expire=None,
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

    def _process_boto_kwargs(
        self,
        boto_kwargs: T.Optional[dict] = None,
    ) -> T.Tuple[T_DATA, str, T.Union[str, T.Tuple[str, ...]], str]:
        """
        对 boto kwargs 进行预处理, 并且根据是否需要从 boto kwargs 中提取额外的 cache key
        的情况来决定 index_name, data_cache_key, query_cache_tag 的值.

        - index_name: 这个 dataset 的 whoosh index 名字
        - data_cache_key: 用于标记数据集已经被 index 的 cache key, 同时会和 query
            中的参数一起构建出 query cache key.
        - query_cache_tag: 无论 query 的参数是什么, 都是用这个 tag, 以便于对其进行批量删除.
        """
        # 获取最终的 boto kwargs
        final_boto_kwargs = self.request._merge_boto_kwargs(boto_kwargs, self.context)
        if self.request.cache_key:
            more_cache_keys: T.List[str] = self.request._get_additional_cache_key(
                final_boto_kwargs
            )
            more_cache_key: str = get_md5_hash(SEP.join(more_cache_keys))

            # index name is the boto + resource + boto kwargs
            index_name = SEP.join((self.index_name, more_cache_key))
            # data cache key is the boto + resource + boto kwargs
            data_cache_key = (self.base_query_cache_key, *more_cache_keys)
            # query cache tag is the boto + resource + boto kwargs
            query_cache_tag = SEP.join((self.base_query_cache_tag, *more_cache_keys))
        else:
            # index name is boto + resource
            index_name = self.index_name
            # data cache key is the boto + resource
            data_cache_key = self.base_query_cache_key
            # query cache tag is the boto + resource
            query_cache_tag = self.base_query_cache_tag

        return (
            final_boto_kwargs,
            index_name,
            data_cache_key,
            query_cache_tag,
        )

    @contextlib.contextmanager
    def _temp_sayt(
        self,
        index_name: str,
        cache_key: str,
        cache_tag: str,
    ):
        """
        Temporarily change the index name, cache key and cache tag of the
        sayt dataset object, and revert it back at the end.
        """
        existing_index_name = self.sayt_dataset.index_name
        existing_cache_key = self.sayt_dataset.cache_key
        existing_cache_tag = self.sayt_dataset.cache_tag
        try:
            self.sayt_dataset.index_name = index_name
            self.sayt_dataset.cache_key = cache_key
            self.sayt_dataset.cache_tag = cache_tag
            yield self
        finally:
            self.sayt_dataset.index_name = existing_index_name
            self.sayt_dataset.cache_key = existing_cache_key
            self.sayt_dataset.cache_tag = existing_cache_tag

    def _refresh_data(
        self,
        final_boto_kwargs: T.Optional[dict] = None,
    ):
        """
        Pull the data via boto3 API call again,
        """
        with TimeTimer(display=False) as timer:
            self.sayt_dataset.remove_index()
        logger.info(f"remove index, elapsed: {timer.elapsed:.3f}s")

        with TimeTimer(display=False) as timer:
            self.sayt_dataset.remove_cache()
        logger.info(f"remove cache, elapsed: {timer.elapsed:.3f}s")

        self.cache.delete(self.sayt_dataset.cache_key)

        with TimeTimer(display=False) as timer:
            res_list = self.request.send(self.bsm, _boto_kwargs=final_boto_kwargs)
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
        # print(doc_list)
        # print(doc_list[0])
        logger.info(f"pull data, elapsed: {timer.elapsed:.3f}s")
        logger.info(f"got {len(doc_list)} documents")
        self.cache.set(
            self.sayt_dataset.cache_key,
            1,
            expire=self.cache_expire,
            tag=self.data_cache_tag,
        )
        with TimeTimer(display=False) as timer:
            logger.info(f"build {self.sayt_dataset.index_name!r} index")
            self.sayt_dataset.build_index(doc_list, rebuild=False)
        logger.info(f"build index, elapsed: {timer.elapsed:.3f}s")

    def _search(
        self,
        q: str,
        limit: int = 20,
    ) -> Result:
        logger.info(f"search on {self.sayt_dataset.index_name!r} index")
        result = self.sayt_dataset.search(q, limit=limit, simple_response=False)
        for hit in result["hits"]:
            url = self.url.get(document=hit["_source"], aws_console=self.aws_console)
            hit["_source"][CONSOLE_URL] = url
        elapsed = result["took"] / 1000
        with logger.indent():
            logger.info(f"search time, elapsed: {elapsed:.3f}s")
            logger.info(f"hit {result['size']} docs.")
            logger.info(f"hit cache: {result['cache']}.")
            if result["size"]:
                logger.info(f"first doc: {result['hits'][0]['_source']}")
        return result

    @staticmethod
    def _simplify_result(result: Result) -> T.List[dict]:  # pragma: no cover
        return [hit["_source"] for hit in result["hits"]]

    def search(
        self,
        q: str,
        limit: int = 20,
        boto_kwargs: T.Optional[dict] = None,
        refresh_data: bool = False,
        simple_response: bool = False,
        verbose: bool = False,
    ) -> T.Union[Result, T.List[dict]]:
        """
        The main public API for AWS Resource Search.

        :param q:
        :param limit:
        :param boto_kwargs:
        :param refresh_data:
        :param verbose:
        """
        with logger.disabled(disable=not verbose):
            logger.ruler("start")

            logger.info("search info:")
            with logger.indent():
                account_or_profile, region = self._bsm_fingerprint
                logger.info(
                    f"search AWS {self.service_id} {self.resource_type} "
                    f"on {account_or_profile} {region}"
                )
                logger.info(f"query: {q!r}")
                (
                    final_boto_kwargs,
                    index_name,
                    data_cache_key,
                    query_cache_tag,
                ) = self._process_boto_kwargs(boto_kwargs)
                logger.info(f"final_boto_kwargs = {final_boto_kwargs!r}")

            logger.info("index, cache info:")
            with logger.indent():
                logger.info(f"index_name = {index_name!r}")
                logger.info(f"data_cache_key = {data_cache_key!r}")
                logger.info(f"query_cache_tag = {query_cache_tag!r}")

            with self._temp_sayt(
                index_name=index_name,
                cache_key=data_cache_key,
                cache_tag=query_cache_tag,
            ):
                if refresh_data or data_cache_key not in self.cache:
                    logger.info("refreshing data ...")
                    with logger.indent():
                        self._refresh_data(final_boto_kwargs)
                result = self._search(q=q, limit=limit)

            if simple_response:  # pragma: no cover
                result = self._simplify_result(result)
            logger.ruler("end")
        return result

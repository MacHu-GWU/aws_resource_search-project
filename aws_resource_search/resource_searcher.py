# -*- coding: utf-8 -*-

import typing as T
import dataclasses
import contextlib
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
from .data.types import T_DATA
from .data.request import Request
from .data.output import Attribute, extract_output
from .data.document import Field, extract_document
from .data.url import Url


def get_boto_session_fingerprint(bsm: "BotoSesManager") -> str:
    """
    Get the logical unique fingerprint of the boto3 session. It is used in
    the index name and cache key.
    """
    parts = []
    if bsm.profile_name is None:
        parts.append(bsm.aws_account_id)
        parts.append(bsm.aws_region)
    else:
        parts.append(bsm.profile_name)
        if bsm.aws_region is not None:
            parts.append(bsm.aws_region)
    return SEP.join(parts)


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
        return SEP.join(
            [
                get_boto_session_fingerprint(self.bsm),
                self.service_id,
                self.resource_type,
            ]
        )

    @cached_property
    def cache_key(self) -> str:
        """
        用于缓存 API Call 的结果的 key. 由你所用的 boto session 的 fingerprint,
        以及你所要搜索的资源的 service_id, resource_type 组成. 这个 key 最终也会被用于
        构成 Query 结果的 cache key.
        """
        return SEP.join(
            [
                get_boto_session_fingerprint(self.bsm),
                self.service_id,
                self.resource_type,
            ]
        )

    @cached_property
    def cache_tag(self) -> str:
        """
        这个 Tag 是用于在清除缓存时, 批量清除所有带有这个 Tag 的缓存的. 我们只有在数据集缓存
        过期后, 才需要清理掉所有这个数据集所有的 Query 的缓存. 同样, 这个 Tag 也是由
        boto session 的 fingerprint, service_id, resource_type 组成.
        """
        return SEP.join(
            [
                get_boto_session_fingerprint(self.bsm),
                self.service_id,
                self.resource_type,
            ]
        )

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

    def _process_boto_kwargs(
        self,
        boto_kwargs: T.Optional[dict] = None,
    ) -> T.Tuple[T_DATA, str, T.Union[str, T.Tuple[str, ...]], str]:
        """
        Sometime the :meth:`ResourceSearcher.index_name` / :meth:`ResourceSearcher.cache_key`
        is not enough to isolate boto API response based on different arguments.
        For example, the AWS Glue get_tables method requires the database name as an argument.
        We should use the ``ResourceSearcher.cache_key`` / ``ResourceSearcher.cache_key``,
        plus the database name as the index name / cache key.

        :param boto_kwargs: The user provided boto3 API call arguments, which will
            be used to generate the final boto kwargs.

        :return: tuple of final_boto_kwargs, index_name_for_data_pull, cache_key_for_data_pull,
            cache_tag_for_cache_remove
        """
        final_boto_kwargs = self.request._merge_boto_kwargs(boto_kwargs, self.context)
        more_cache_keys = self.request._get_additional_cache_key(final_boto_kwargs)
        index_name_for_data_pull = SEP.join((self.index_name, *more_cache_keys))
        cache_key_for_data_pull = (self.cache_key, *more_cache_keys)
        cache_tag_for_cache_remove = SEP.join((self.cache_tag, *more_cache_keys))
        return (
            final_boto_kwargs,
            index_name_for_data_pull,
            cache_key_for_data_pull,
            cache_tag_for_cache_remove,
        )

    @contextlib.contextmanager
    def _temp_sayt(
        self,
        index_name: str,
        cache_key: str,
        cache_tag: str,
    ):
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
        with TimeTimer(display=False) as timer:
            self.sayt_dataset.remove_index()
        logger.info(f"remove index, elapsed: {timer.elapsed:.3f}s")

        with TimeTimer(display=False) as timer:
            self.sayt_dataset.remove_cache()
        logger.info(f"remove cache, elapsed: {timer.elapsed:.3f}s")

        with TimeTimer(display=False) as timer:
            res_list = self.request.send(self.bsm, _boto_kwargs=final_boto_kwargs)
            res_list = res_list.all()
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
        # print(doc_list[0])
        logger.info(f"pull data, elapsed: {timer.elapsed:.3f}s")
        logger.info(f"got {len(doc_list)} documents")
        self.cache.set(
            self.cache_key,
            1,
            expire=self.cache_expire,
            tag=self.cache_tag,
        )
        with TimeTimer(display=False) as timer:
            logger.info(f"build {self.sayt_dataset.normalized_index_name!r} index")
            self.sayt_dataset.build_index(doc_list, rebuild=False)
        logger.info(f"build index, elapsed: {timer.elapsed:.3f}s")

    def _search(
        self,
        q: str,
        limit: int = 20,
    ) -> Result:
        logger.info(f"search on {self.sayt_dataset.normalized_index_name!r} index")
        result = self.sayt_dataset.search(q, limit=limit, simple_response=False)
        for hit in result["hits"]:
            url = self.url.get(document=hit["_source"], aws_console=self.aws_console)
            hit["_source"][CONSOLE_URL] = url
        elapsed = result["took"] / 1000
        with logger.indent():
            logger.info(f"search time, elapsed: {elapsed:.3f}s")
            logger.info(f"hit {result['size']} docs.")
        return result

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
            logger.info(f"query: {q!r}")
            if self.request.cache_key:
                (
                    final_boto_kwargs,
                    index_name_for_data_pull,
                    cache_key_for_data_pull,
                    cache_tag_for_cache_remove,
                ) = self._process_boto_kwargs(boto_kwargs)
                need_temp_index_name_and_cache_key = True
            else:
                final_boto_kwargs = self.request._merge_boto_kwargs(
                    boto_kwargs, self.context
                )
                index_name_for_data_pull = self.index_name
                cache_key_for_data_pull = self.cache_key
                cache_tag_for_cache_remove = self.cache_tag
                need_temp_index_name_and_cache_key = False
            logger.info(f"final_boto_kwargs = {final_boto_kwargs!r}")
            logger.info(f"index_name_for_data_pull = {index_name_for_data_pull!r}")
            logger.info(f"cache_key_for_data_pull = {cache_key_for_data_pull!r}")
            logger.info(f"cache_tag_for_cache_remove = {cache_tag_for_cache_remove!r}")
            if refresh_data or cache_key_for_data_pull not in self.cache:
                logger.info("refreshing data ...")
                if need_temp_index_name_and_cache_key:
                    logger.info(
                        f"need_temp_index_name_and_cache_key: {need_temp_index_name_and_cache_key}",
                        indent=1,
                    )
                    with self._temp_sayt(
                        index_name=index_name_for_data_pull,
                        cache_key=cache_key_for_data_pull,
                        cache_tag=cache_tag_for_cache_remove,
                    ):
                        with logger.indent():
                            self._refresh_data(final_boto_kwargs)
                        result = self._search(q=q, limit=limit)
                else:
                    with logger.indent():
                        self._refresh_data(final_boto_kwargs)
                    result = self._search(q=q, limit=limit)
            else:
                result = self._search(q=q, limit=limit)

            if simple_response: # pragma: no cover
                result = [hit["_source"] for hit in result["hits"]]
            return result

# -*- coding: utf-8 -*-

import typing as T
import copy
import dataclasses

from boto_session_manager import BotoSesManager
import sayt.api as sayt

from .paths import dir_index, dir_cache
from .utils import get_md5_hash
from .base_model import BaseModel
from .downloader import ResultPath, list_resources
from .documents.api import T_ARS_RESOURCE_DOCUMENT


SEP = "____"

T_MORE_CACHE_KEY = T.Callable[[sayt.T_DOCUMENT], T.List[str]]


def preprocess_query(query: T.Optional[str]) -> str:
    """
    Preprocess query, automatically add fuzzy search term if applicable.
    """
    delimiter = ".-_@+"
    if query:
        for char in delimiter:
            query = query.replace(char, " ")
        words = list()
        for word in query.split():
            if word.strip():
                word = word.strip()
                if len(word) == 1:
                    if word == "*":
                        words.append(word)
                else:
                    try:
                        if word[-2] != "~" and not word.endswith("!~"):
                            word = f"{word}~1"
                    except IndexError:
                        word = f"{word}~1"
                    words.append(word)
        if words:
            return " ".join(words)
        else:
            return "*"
    else:
        return "*"


@dataclasses.dataclass
class BaseSearcher(BaseModel, T.Generic[T_ARS_RESOURCE_DOCUMENT]):
    """
    todo: docstring

    :param service:
    :param method:
    :param is_paginator:
    :param default_boto_kwargs:
    :param result_path:
    :param doc_class:
    :param resource_type:
    :param fields:
    :param cache_expire:
    :param more_cache_key:
    :param bsm:
    """

    # list resources related
    service: str = dataclasses.field()
    method: str = dataclasses.field()
    is_paginator: bool = dataclasses.field()
    default_boto_kwargs: T.Optional[dict] = dataclasses.field()
    result_path: ResultPath = dataclasses.field()
    # extract document related
    doc_class: T.Type[T_ARS_RESOURCE_DOCUMENT] = dataclasses.field()
    # search related
    resource_type: str = dataclasses.field()
    fields: T.List[sayt.T_Field] = dataclasses.field()
    cache_expire: int = dataclasses.field()
    more_cache_key: T.Optional[T_MORE_CACHE_KEY] = dataclasses.field()
    # boto session
    bsm: T.Optional[BotoSesManager] = dataclasses.field(default=None)

    def _get_bsm(
        self,
        bsm: T.Optional[BotoSesManager] = None,
    ) -> BotoSesManager:
        """
        Preprocess the bsm arguments. Allow user to override the default bsm.
        """
        if bsm is None:
            final_bsm = self.bsm
        else:
            final_bsm = bsm
        if not isinstance(final_bsm, BotoSesManager):
            raise TypeError(f"bsm must be BotoSesManager, not {type(bsm)}")
        return final_bsm

    def _get_bsm_fingerprint(
        self,
        bsm: BotoSesManager,
    ) -> T.Tuple[str, T.Optional[str]]:
        """
        Get the logical unique fingerprint of the boto3 session. It will be
        used in the index name and cache key naming convention.
        """
        if str(bsm.profile_name) == "Sentinel('NOTHING')":
            account_or_profile = bsm.aws_account_id
        else:  # pragma: no cover
            account_or_profile = bsm.profile_name
        if bsm.aws_region is None:  # pragma: no cover
            region = "unknown-region"
        else:
            region = bsm.aws_region
        return account_or_profile, region

    def _get_final_boto_kwargs(self, boto_kwargs: T.Optional[dict] = None) -> dict:
        """
        Get the final boto3 api call kwargs by merging the default boto3 api
        and kwargs overrides
        """
        if self.default_boto_kwargs:
            final_boto_kwargs = copy.deepcopy(self.default_boto_kwargs)
        else:
            final_boto_kwargs = {}
        if boto_kwargs is not None:
            final_boto_kwargs.update(boto_kwargs)
        return final_boto_kwargs

    def _get_ds(
        self,
        bsm: BotoSesManager,
        final_boto_kwargs: dict,
    ) -> sayt.DataSet:
        """
        Get the corresponding ``sayt.DataSet`` object.
        """
        account_or_profile, region = self._get_bsm_fingerprint(bsm=bsm)
        if self.more_cache_key is None:
            index_name = SEP.join([account_or_profile, region, self.resource_type])
        else:
            index_name = SEP.join(
                [
                    account_or_profile,
                    region,
                    self.resource_type,
                    get_md5_hash(SEP.join(self.more_cache_key(final_boto_kwargs))),
                ]
            )
        cache_key = index_name
        cache_tag = index_name

        def downloader():
            resource_data_iter_proxy = list_resources(
                bsm=bsm,
                service=self.service,
                method=self.method,
                is_paginator=self.is_paginator,
                boto_kwargs=final_boto_kwargs,
                result_path=self.result_path,
            )
            for document in self.doc_class.from_many_resources(
                resources=resource_data_iter_proxy,
                bsm=bsm,
                boto_kwargs=final_boto_kwargs,
            ):
                doc_dict = document.to_dict()
                # print(doc_dict) # for DEBUG ONLY
                yield doc_dict

        return sayt.DataSet(
            dir_index=dir_index,
            index_name=index_name,
            fields=self.fields,
            dir_cache=dir_cache,
            cache_key=cache_key,
            cache_tag=cache_tag,
            cache_expire=self.cache_expire,
            downloader=downloader,
        )

    def search(
        self,
        query: str = "*",
        limit: int = 50,
        boto_kwargs: T.Optional[dict] = None,
        refresh_data: bool = False,
        simple_response: bool = True,
        verbose: bool = False,
        bsm: T.Optional[BotoSesManager] = None,
    ) -> T.Union[sayt.T_Result, T.List[T_ARS_RESOURCE_DOCUMENT]]:
        """
        Search the dataset.

        :param query: query string
        :param limit: the max number of results to return
        :param boto_kwargs: additional boto3 keyword arguments
        :param refresh_data: force to refresh the data
        :param simple_response: if True, then return a list of ``T_ARS_RESOURCE_DOCUMENT``
            objects, otherwise return the elasticsearch liked result.
        :param verbose: whether to print the log
        :param bsm: you can explicitly use a ``BotoSesManager`` object to override
            the default one you defined when creating the :class:`aws_resource_search.base_searcher.BaseSearcher`` object.
        """
        final_boto_kwargs = self._get_final_boto_kwargs(boto_kwargs=boto_kwargs)
        ds = self._get_ds(
            bsm=self._get_bsm(bsm),
            final_boto_kwargs=final_boto_kwargs,
        )
        final_query = preprocess_query(query)
        result = ds.search(
            query=final_query,
            limit=limit,
            simple_response=False,
            refresh_data=refresh_data,
            verbose=verbose,
        )
        if simple_response:
            return [self.doc_class.from_dict(dct["_source"]) for dct in result["hits"]]
        else:
            return result


T_SEARCHER = T.TypeVar("T_SEARCHER", bound=BaseSearcher)

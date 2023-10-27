# -*- coding: utf-8 -*-

"""
Utility class and function in this module will be used in
:mod:`aws_resource_search.res` module.
"""

import typing as T
import copy
import dataclasses
from datetime import datetime

import jmespath
import aws_console_url.api as acu
import sayt.api as sayt
import zelfred.api as zf
from iterproxy import IterProxy
from boto_session_manager import BotoSesManager

from .model import BaseModel
from .utils import get_md5_hash
from .paths import dir_index, dir_cache


# ------------------------------------------------------------------------------
# Boto3 API Call
# ------------------------------------------------------------------------------
T_RESULT_DATA = T.Union[sayt.T_DOCUMENT, str]


class ResourceIterproxy(IterProxy[T_RESULT_DATA]):
    pass


@dataclasses.dataclass
class ResultPath(BaseModel):
    """
    Defines how to extract list of AWS resource data from boto3 API call response.

    For example, the result path for ``s3_client.list_buckets`` is ``Buckets``,
    and the result path for ``ec2_client.describe_instances`` is ``Reservations[].Instances[]``.

    :param path: The result path. It will return an empty list if the result path
        doesn't exist in the response.
    """

    path: str = dataclasses.field()
    _compiled: jmespath.parser.ParsedResult = dataclasses.field(init=False)

    def __post_init__(self):
        self._compiled = jmespath.compile(self.path + " || `[]`")

    def extract(self, response: dict) -> T.Iterator[T_RESULT_DATA]:
        """
        Ext

        :param response: boto3 API response

        :return: for example, for s3_client.list_buckets, it will return::

            [
                {
                    'Name': 'string',
                    'CreationDate': datetime(2015, 1, 1)
                },
                ...
            ]
        """
        return self._compiled.search(response)


def list_resources(
    bsm: BotoSesManager,
    service: str,
    method: str,
    is_paginator: bool,
    boto_kwargs: T.Optional[dict],
    result_path: ResultPath,
) -> ResourceIterproxy:
    """
    Call boto3 API to list AWS resources.

    Example:

    .. code-block:: python

        >>> for iam_group_data in list_resources(
        ...     bsm=self.bsm,
        ...     service="iam",
        ...     method="list_groups",
        ...     is_paginator=True,
        ...     boto_kwargs=dict(
        ...         PaginationConfig=dict(
        ...             MaxItems=9999,
        ...             PageSize=1000,
        ...         )
        ...     ),
        ...     result_path=ResultPath(path="Groups"),
        ... ):
        ...     print(iam_group_data)
    """

    def func():
        if boto_kwargs is None:
            kwargs = {}
        else:
            kwargs = boto_kwargs
        client = bsm.get_client(service)
        if is_paginator:
            paginator = client.get_paginator(method)
            for response in paginator.paginate(**kwargs):
                yield from result_path.extract(response)
        else:
            response = getattr(client, method)(**kwargs)
            yield from result_path.extract(response)

    return ResourceIterproxy(func())


# ------------------------------------------------------------------------------
# Document
# ------------------------------------------------------------------------------


@dataclasses.dataclass
class BaseDocument(BaseModel):
    raw_data: T_RESULT_DATA = dataclasses.field()

    @classmethod
    def from_resource(
        cls,
        resource: T_RESULT_DATA,
        bsm: BotoSesManager,
        boto_kwargs: dict,
    ):
        """
        Create a document object from the boto3 API response data.
        Since the API response data is based on the bsm object and boto_kwargs,
        we also need those information to create the document object.

        For example, ``s3_client.list_buckets`` api returns::

            {
                'Name': '...',
                'CreationDate': datetime.datetime(...)
            }

        The implementation should be::

            >>> @dataclasses.dataclass
            ... class S3BucketDocument(BaseDocument):
            ...
            ...     id: str = dataclasses.field()
            ...     name: str = dataclasses.field()
            ...     creation_date: str = dataclasses.field()
            ...
            ...     @classmethod
            ...     def from_resource(cls, resource: T_RESULT_DATA):
            ...         return cls(
            ...             raw_data=resource,
            ...             id=resource["Name"],
            ...             name=resource["Name"],
            ...             creation_date=resource["CreationDate"].isoformat(),
            ...         )
        """
        raise NotImplementedError

    @property
    def title(self) -> str:
        """
        The title in the zelfred UI.
        """
        raise NotImplementedError

    @property
    def subtitle(self) -> str:
        """
        The subtitle in the zelfred UI.
        """
        return "No Subtitle"

    @property
    def uid(self) -> str:
        """
        The uid in the zelfred UI.
        """
        return self.title

    @property
    def autocomplete(self) -> str:
        """
        Autocomplete text for the zelfred UI.
        """
        return ""

    @property
    def arn(self) -> str:
        """
        AWS Resource ARN, if applicable. User can tap 'Ctrl + A' to copy the ARN.
        """
        raise NotImplementedError

    def get_console_url(self, console: acu.AWSConsole) -> str:
        """
        AWS Console URL, if applicable, User can tap 'Enter' to open in browser.
        """
        raise NotImplementedError

    @property
    def details(self) -> T.List[zf.T_ITEM]:
        """
        Additional details for the resource, it will be rendered in the
        dropdown menu. User can tap tab 'Ctrl + P' to view the details,
        and tap 'F1' to go back to the previous view.
        """
        raise NotImplementedError


T_DOCUMENT_OBJ = T.TypeVar("T_DOCUMENT_OBJ", bound=BaseDocument)


def extract_datetime(
    resource: T_RESULT_DATA,
    jpath: str,
    default: str = "No datetime",
) -> str:
    """
    Example:

        >>> extract_datetime({"CreateDate": datetime(2021, 1, 1)}, path="CreateDate")
        "2021-01-01T00:00:00"
    """
    res = jmespath.search(jpath, resource)
    if res is None:
        return default
    elif isinstance(res, datetime):
        return res.isoformat()
    else:
        return res


# ------------------------------------------------------------------------------
# Searcher
# ------------------------------------------------------------------------------
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
class Searcher(BaseModel):
    """
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

    # list resources
    service: str = dataclasses.field()
    method: str = dataclasses.field()
    is_paginator: bool = dataclasses.field()
    default_boto_kwargs: T.Optional[dict] = dataclasses.field()
    result_path: ResultPath = dataclasses.field()
    # extract document
    doc_class: T.Type[T_DOCUMENT_OBJ] = dataclasses.field()
    # search
    resource_type: str = dataclasses.field()
    fields: T.List[sayt.T_Field] = dataclasses.field()
    cache_expire: int = dataclasses.field()
    more_cache_key: T.Optional[T_MORE_CACHE_KEY] = dataclasses.field()

    bsm: T.Optional[BotoSesManager] = dataclasses.field(default=None)

    def _get_bsm(self, bsm: T.Optional[BotoSesManager] = None) -> BotoSesManager:
        """
        Preprocess the bsm arguments.
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
            for resource in list_resources(
                bsm=bsm,
                service=self.service,
                method=self.method,
                is_paginator=self.is_paginator,
                boto_kwargs=final_boto_kwargs,
                result_path=self.result_path,
            ):
                doc_dict = self.doc_class.from_resource(
                    resource=resource,
                    bsm=bsm,
                    boto_kwargs=final_boto_kwargs,
                ).to_dict()
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
        limit: int = 20,
        boto_kwargs: T.Optional[dict] = None,
        refresh_data: bool = False,
        simple_response: bool = True,
        verbose: bool = False,
        bsm: T.Optional[BotoSesManager] = None,
    ) -> T.Union[sayt.T_Result, T.List[T_DOCUMENT_OBJ]]:
        """
        Search the dataset.

        :param query: query string
        :param limit: the max number of results to return
        :param boto_kwargs: additional boto3 keyword arguments
        :param refresh_data: force to refresh the data
        :param simple_response: if True, then return a list of ``T_DOCUMENT_OBJ``
            objects, otherwise return the elasticsearch liked result.
        :param verbose: whether to print the log
        :param bsm: you can explicitly use a ``BotoSesManager`` object to override
            the default one you defined when creating the :class:`Searcher`` object.
        """
        if self.default_boto_kwargs:
            final_boto_kwargs = copy.deepcopy(self.default_boto_kwargs)
        else:
            final_boto_kwargs = {}
        if boto_kwargs is not None:
            final_boto_kwargs.update(boto_kwargs)
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
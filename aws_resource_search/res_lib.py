# -*- coding: utf-8 -*-

"""
Utility class and function in this module will be used in writing
:mod:`aws_resource_search.res` module nice and clean.
"""

import typing as T
import uuid
import json
import copy
import dataclasses
import contextlib
from pathlib import Path
from datetime import datetime, timezone

import jmespath
import botocore.exceptions
import aws_console_url.api as acu
import sayt.api as sayt
import zelfred.api as zf
from iterproxy import IterProxy
from boto_session_manager import BotoSesManager

try:
    import pyperclip
except ImportError:  # pragma: no cover
    pass

from .model import BaseModel
from .utils import get_md5_hash
from .paths import dir_index, dir_cache
from .terminal import ShortcutEnum, format_key_value
from .compat import TypedDict


if T.TYPE_CHECKING:  # pragma: no cover
    from .ars import ARS


# ------------------------------------------------------------------------------
# Boto3 API Call
# ------------------------------------------------------------------------------
T_RESULT_DATA = T.Union[sayt.T_DOCUMENT, str]


class ResourceIterproxy(IterProxy[T_RESULT_DATA]):
    """
    Advanced iterator object for AWS resource data in boto3 API response.

    Ref: https://github.com/MacHu-GWU/iterproxy-project
    """


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
        Extract list of AWS resource data from boto3 API call response.

        :param response: boto3 API response

        :return: for example, for s3_client.list_buckets, it will return.

        .. code-block:: python

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
        ...     bsm=bsm,
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
def get_utc_now() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def human_readable_elapsed(sec: int) -> str:
    if sec < 60:
        return f"{sec} sec"
    elif sec < 3600:
        div, mod = divmod(sec, 60)
        if mod:
            return f"{div} min {mod} sec"
        else:
            return f"{div} min"
    elif sec < 86400:
        div, mod = divmod(sec, 3600)
        if mod:
            return f"{div} hour {mod / 60:.1f} min"
        else:
            return f"{div} hour"
    else:
        div, mod = divmod(sec, 86400)
        if mod:
            return f"{div} day {mod / 3600:.1f} hour"
        else:
            return f"{div} day"


def get_none_or_default(
    data: T.Any,
    path: str,
    default: T.Optional[T.Any] = None,
) -> T.Any:
    """
    A helper method to get value from ``data``. If the value doesn't exist,
    it will return the default value.

    Example:

        >>> doc = {"a": 1, "b": {"c": 3})
        >>> get_none_or_default(data, "a")
        1
        >>> get_none_or_default(data, "d")
        None
        >>> get_none_or_default(data, "d", "hello")
        "hello"
        >>> get_none_or_default(data, "b.c")
        3
        >>> get_none_or_default(data, "b.d")
        None
        >>> get_none_or_default(data, "b.d", "hello")
        "hello"
        >>> get_none_or_default(data, "c.e")
        None
        >>> get_none_or_default(data, "c.e", "hello")
        "hello"

    :param path: jmespath syntax
    :param default: default value if the value doesn't exist
    """
    value = jmespath.search(path, data)
    return value if value else default


def get_description(
    data: T.Any,
    path: str,
    default: T.Optional[str] = "No description",
) -> str:
    return get_none_or_default(data, path, default)


def get_datetime(
    data: T.Any,
    path: str,
    default: datetime = datetime(1970, 1, 1, tzinfo=timezone.utc),
    as_utc: bool = True,
) -> datetime:
    """
    Extract isoformat datetime string from a dictionary using Jmespath.

    Example:

        >>> get_datetime({"CreateDate": datetime(2021, 1, 1)}, path="CreateDate")
        datetime(2021, 1, 1)
    """
    res = jmespath.search(path, data)
    if bool(res) is False:
        return default
    elif isinstance(res, datetime):
        if as_utc:
            if res.tzinfo is None:
                return res.replace(tzinfo=timezone.utc)
            else:
                return res.astimezone(timezone.utc)
        else:
            return res
    else:  # pragma: no cover
        raise TypeError


def to_simple_fmt(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_datetime_isofmt(
    data: T.Any,
    path: str,
    default: str = "No datetime",
) -> str:
    """
    Extract isoformat datetime string from a dictionary using Jmespath.

    Example:

        >>> get_datetime_isofmt({"CreateDate": datetime(2021, 1, 1)}, path="CreateDate")
        "2021-01-01T00:00:00"
    """
    res = jmespath.search(path, data)
    if bool(res) is False:
        return default
    elif isinstance(res, datetime):
        return res.isoformat()
    else:
        return res


def get_datetime_simplefmt(
    data: T.Any,
    path: str,
    default: str = "No datetime",
) -> str:
    """
    Extract isoformat datetime string from a dictionary using Jmespath.

    Example:

        >>> get_datetime_simplefmt({"CreateDate": datetime(2021, 1, 1, microsecond=123000)}, path="CreateDate")
        "2021-01-01 00:00:00"
    """
    res = jmespath.search(path, data)
    if bool(res) is False:
        return default
    elif isinstance(res, datetime):
        if res.tzinfo is None:
            res = res.replace(tzinfo=timezone.utc)
        return res.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return res


@dataclasses.dataclass
class BaseDocument(BaseModel):
    """
    This is the base class for AWS resource documents. A 'document' is a
    searchable object stored in the index, representing the metadata of
    an AWS resource.

    **Guide, how to subclass this correctly**

    To create a per-AWS-resource document class, you need to
    inherit from this class. For example, you can define a document class for
    S3 bucket like this:

        >>> @dataclasses.dataclass
        >>> class S3BucketDocument(BaseDocument):
        ...     id: str = dataclasses.field()
        ...     name: str = dataclasses.field()

    The base document has a mandatory field ``raw_data``, which is used to store
    the data in the boto3 API call response. For example, for
    `s3_client.list_buckets <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_buckets.html>`,
    the raw data is:

    .. code-block:: python

        {
            'Name': 'string',
            'CreationDate': datetime(2015, 1, 1)
        }

    Besides ``raw_data``, the base document also has two mandatory fields ``id``
    and ``name``. The ``id`` field is used to uniquely identify the document,
    and it is also a searchable ``IdField``. The ``name`` field is a human-firendly
    name, and it is also an n-gram searchable ``NgramWordsField``. Both ``id``
    and ``name`` should be able to extracted from ``raw_data``. However, we still
    need to store the copy of its value in this attribute, because we need to
    index them as searchable fields. You can define more searchable attribute
    as you need.

    If an attribute is not searchable, you can define it as a property method.

    In your subclass, you must implement the following methods.
    Please read the docstrings to understand their functionality.

    - :meth:`from_resource`
    - :meth:`title`
    - :meth:`arn`
    - :meth:`get_console_url`
    """

    raw_data: T_RESULT_DATA = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()

    @classmethod
    def from_resource(
        cls,
        resource: T_RESULT_DATA,
        bsm: BotoSesManager,
        boto_kwargs: dict,
    ):
        """
        Create a document object from the boto3 API response data.
        Since the API response data relies on both the 'bsm' object
        and 'boto_kwargs,' we also require this information to
        create the document object.

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

    @classmethod
    def from_many_resources(
        cls,
        resources: ResourceIterproxy,
        bsm: BotoSesManager,
        boto_kwargs: dict,
    ):
        for resource in resources:
            yield cls.from_resource(
                resource=resource,
                bsm=bsm,
                boto_kwargs=boto_kwargs,
            )

    @property
    def title(self) -> str:
        """
        The title in the zelfred UI.

        For example, you want to use the S3 bucket name as the title::


            >>> @dataclasses.dataclass
            ... class S3BucketDocument(BaseDocument):
            ...     @property
            ...     def title(self) -> str:
            ...         return f"bucket name = {self.name}"
        """
        raise NotImplementedError

    @property
    def subtitle(self) -> str:
        """
        The subtitle in the zelfred UI.

        The default subtitle is the help text to show the user how to interact with the UI.
        """
        return (
            f"🌐 {ShortcutEnum.ENTER} to open url, "
            f"📋 {ShortcutEnum.CTRL_A} to copy arn, "
            f"🔗 {ShortcutEnum.CTRL_U} to copy url, "
            f"👀 {ShortcutEnum.CTRL_P} to view details."
        )

    @property
    def short_subtitle(self) -> str:
        """
        A shorter version of subtitle.
        """
        return (
            f"🌐 {ShortcutEnum.ENTER}, "
            f"📋 {ShortcutEnum.CTRL_A}, "
            f"🔗 {ShortcutEnum.CTRL_U}, "
            f"👀 {ShortcutEnum.CTRL_P}."
        )

    @property
    def uid(self) -> str:
        """
        The internal uid used for sorting and deduplication in the zelfred UI.
        """
        return uuid.uuid4().hex

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
        msg = f"{self.__class__.__name__} doesn't support ARN"
        raise NotImplementedError(msg)

    def get_console_url(self, console: acu.AWSConsole) -> str:
        """
        AWS Console URL, if applicable, User can tap 'Enter' to open in browser.
        """
        msg = f"{self.__class__.__name__} doesn't support AWS Console url"
        raise NotImplementedError(msg)

    def get_details(self, ars: "ARS") -> T.List[zf.T_ITEM]:
        """
        Additional details for the resource, it will be rendered in the
        dropdown menu. User can tap tab 'Ctrl + P' to view the details,
        and tap 'F1' to go back to the previous view.
        """
        msg = f"{self.__class__.__name__} doesn't support get details"
        raise NotImplementedError(msg)

    def get_initial_detail_items(
        self,
        ars: "ARS",
        arn_field_name: str = "arn",
    ) -> list:
        """
        Most AWS resource detail should have one ARN item that user can tap
        "Ctrl A" to copy and tap "Enter" to open url. Only a few AWS resource
        doesn't support ARN (for example glue job run).
        """
        try:
            return [
                DetailItem.from_detail(
                    name=arn_field_name,
                    value=self.arn,
                    url=self.get_console_url(ars.aws_console),
                ),
            ]
        except NotImplementedError:
            return []

    @staticmethod
    @contextlib.contextmanager
    def enrich_details(detail_items: list):
        """
        A context manager to add additional detail items. It automatically
        captures boto3 exception and creates debug item.
        """
        try:
            yield None
        except botocore.exceptions.ClientError as e:
            detail_items.append(
                DetailItem.from_error(
                    type=f"{e.operation_name} failed",
                    msg=str(e),
                )
            )

    @staticmethod
    def one_line(obj, na: str = "NA") -> str:
        """
        Convert a python object to one line json string.

        This is usually used in the :meth:`BaseDocument.get_details`` method
        to normalize multiline json object in the UI.
        """
        if obj:
            if isinstance(obj, str):
                if obj.startswith("[") or obj.startswith("{"):
                    return json.dumps(json.loads(obj))
                else:
                    lines = obj.splitlines()
                    if len(lines) > 1:
                        return f"{lines[0]} ..."
                    else:
                        return lines[0]
            else:
                return json.dumps(obj)
        else:
            return na


T_DOCUMENT_OBJ = T.TypeVar("T_DOCUMENT_OBJ", bound=BaseDocument)


# ------------------------------------------------------------------------------
# Searcher
# ------------------------------------------------------------------------------
SEP = "____"

T_MORE_CACHE_KEY = T.Callable[[sayt.T_DOCUMENT], T.List[str]]


_built_in_fields = {"raw_data", "id", "name"}


def define_fields(
    fields: T.List[sayt.T_Field] = None,
    id_field_boost: float = 5.0,
    name_minsize: int = 2,
    name_maxsize: int = 4,
    name_sortable: bool = True,
    name_ascending: bool = True,
) -> T.List[sayt.T_Field]:
    """
    A helper function to define the :attr:`Searcher.fields` property. It comes
    with the default fields: ``raw_data``, ``id``, ``name``.

    1. all document class has a "raw_data" field inherit from res_lib.BaseDocument.
    2. the ``id`` field is the unique identifier of the document. and it is also
        a searchable ``IdField``. this field haves higher weight (in field_boost).
    3. the ``name`` field is a human-firendly name, and it is also an
        n-gram searchable ``NgramWordsField``. the default setting is that
        the result is ordered by name in ascending order
        (in name_sortable and name_ascending).

    :param fields: additional fields to be added.
    :param id_field_boost: parameter for the default fields.
    :param name_minsize: parameter for the default fields.
    :param name_maxsize: parameter for the default fields.
    :param name_sortable: parameter for the default fields.
    :param name_ascending: parameter for the default fields.
    """
    final_fields = [
        sayt.StoredField(name="raw_data"),
        sayt.IdField(name="id", field_boost=id_field_boost, stored=True),
        sayt.NgramWordsField(
            name="name",
            minsize=name_minsize,
            maxsize=name_maxsize,
            stored=True,
            sortable=name_sortable,
            ascending=name_ascending,
        ),
    ]
    if fields:
        final_fields.extend(
            [field for field in fields if field.name not in _built_in_fields]
        )
    return final_fields


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
class Searcher(BaseModel, T.Generic[T_DOCUMENT_OBJ]):
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

    def _get_final_boto_kwargs(self, boto_kwargs: T.Optional[dict] = None) -> dict:
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


# ------------------------------------------------------------------------------
# Custom Item
# ------------------------------------------------------------------------------
@dataclasses.dataclass
class ArsBaseItem(zf.Item):
    """
    Base class for all ``zelfred.Item`` subclasses in ``aws_resource_search``.
    """

    def open_url_or_print(self, ui: zf.UI, url: str):  # pragma: no cover
        """
        Sometime user are in a remote shell and doesn't have default web browser.
        Then we print the url instead.
        """
        try:
            zf.open_url(url)
        except FileNotFoundError as e:
            if "open" in str(e):
                print(
                    f"{ui.terminal.cyan}Your system doesn't support open url in browser to clipboard, "
                    f"we print it here so you can copy manually.{ui.terminal.normal}"
                )
                print(url)
                ui.need_run_handler = False
                raise KeyboardInterrupt
                # raise zf.exc.EndOfInputError(selection=self)
            else:
                raise e

    def copy_or_print(self, ui: zf.UI, text: str):  # pragma: no cover
        """
        Sometime user are in a remote shell and cannot use the clipboard.
        Then we print the value instead.
        """
        try:
            pyperclip.copy(text)
        except pyperclip.PyperclipException:
            print(
                f"{ui.terminal.cyan}Your system doesn't support copy to clipboard, "
                f"we print it here so you can copy manually.{ui.terminal.normal}"
            )
            print(text)
            ui.need_run_handler = False
            raise KeyboardInterrupt
            # raise zf.exc.EndOfInputError(selection=self)

    def post_enter_handler(self, ui: zf.UI):  # pragma: no cover
        ui.wait_next_user_input()

    def post_ctrl_a_handler(self, ui: zf.UI):  # pragma: no cover
        ui.wait_next_user_input()

    def post_ctrl_w_handler(self, ui: zf.UI):  # pragma: no cover
        ui.wait_next_user_input()

    def post_ctrl_u_handler(self, ui: zf.UI):  # pragma: no cover
        ui.wait_next_user_input()

    def post_ctrl_p_handler(self, ui: zf.UI):  # pragma: no cover
        ui.wait_next_user_input()


class DetailItemVariables(TypedDict):
    url: T.Optional[str]
    copy: T.Optional[str]


@dataclasses.dataclass
class DetailItem(ArsBaseItem):
    """
    Represent an item to show the detail of a resource. User can tap
    'Ctrl + P' to enter this view.

    The default user action behaviors are:

    1. tap "Enter" to open the url to verify the detail, if url is not available, do nothing.
    2. tap "Ctrl + A" to copy the detail value text to clipboard. if value is not available, do nothing.
    """

    variables: DetailItemVariables = dataclasses.field(default_factory=dict)

    def enter_handler(self, ui: "zf.UI"):  # pragma: no cover
        if self.variables.get("url"):
            self.open_url_or_print(ui, self.variables["url"])

    def ctrl_a_handler(self, ui: "zf.UI"):  # pragma: no cover
        if self.variables["copy"]:
            self.copy_or_print(ui, self.variables["copy"])

    @classmethod
    def new(
        cls,
        title: str,
        subtitle: str,
        copy: T.Optional[str] = None,
        url: T.Optional[str] = None,
        uid: T.Optional[str] = None,
        autocomplete: T.Optional[str] = None,
    ):
        """
        Create one :class:`DetailItem` that may be can copy text or open url.

        :param name: this is for title
        :param value: this if for copy to clipboard
        :param text: this is for title
        :param url: this is for open url
        :param uid: this is for uid
        """
        kwargs = dict(
            title=title,
            subtitle=subtitle,
            autocomplete=autocomplete,
            variables={"copy": copy, "url": url},
        )
        if uid:
            kwargs["uid"] = uid
        return cls(**kwargs)

    @classmethod
    def from_detail(
        cls,
        name,
        value,
        text: T.Optional[str] = None,
        url: T.Optional[str] = None,
        uid: T.Optional[str] = None,
    ):
        """
        Create one :class:`DetailItem` from structured detail information.

        :param name: this is for title
        :param value: this if for copy to clipboard
        :param text: this is for title
        :param url: this is for open url
        :param uid: this is for uid
        """
        if text is None:
            text = value
        if url:
            subtitle = (
                f"🌐 {ShortcutEnum.ENTER} to open url, 📋 {ShortcutEnum.CTRL_A} to copy."
            )
        else:
            subtitle = f"📋 {ShortcutEnum.CTRL_A} to copy."
        return cls.new(
            title=format_key_value(name, text),
            subtitle=subtitle,
            uid=uid,
            copy=str(value),
            url=url,
        )

    @classmethod
    def from_env_vars(
        cls,
        env_vars: T.Dict[str, str],
        url: T.Optional[str] = None,
    ) -> T.List["DetailItem"]:
        """
        Create MANY :class:`DetailItem` from environment variable key value pairs.
        """
        items = [
            cls.new(
                title=f"🎯 env var: {format_key_value(k, v)}",
                subtitle=f"🌐 {ShortcutEnum.ENTER} to open url, 📋 {ShortcutEnum.CTRL_A} to copy value.",
                uid=f"env_var {k}",
                copy=v,
                url=url,
            )
            for k, v in env_vars.items()
        ]
        if len(items):
            return items
        else:
            return [
                cls.new(
                    title=f"🏷 env var: 🔴 No environment variable found",
                    subtitle=f"no environment variable found",
                    uid=f"no environment variable found",
                    url=url,
                )
            ]

    @classmethod
    def from_tags(
        cls,
        tags: T.Dict[str, str],
        url: T.Optional[str] = None,
    ) -> T.List["DetailItem"]:
        """
        Create MANY :class:`DetailItem` from AWS resource tag key value pairs.
        """
        items = [
            cls.new(
                title=f"🏷 tag: {format_key_value(k, v)}",
                subtitle=f"🌐 {ShortcutEnum.ENTER} to open url, 📋 {ShortcutEnum.CTRL_A} to copy value.",
                uid=f"tag {k}",
                copy=v,
                url=url,
            )
            for k, v in tags.items()
        ]
        if len(items):
            return items
        else:
            return [
                cls.new(
                    title=f"🏷 tag: 🔴 No tag found",
                    subtitle=f"no tag found",
                    uid=f"no tag found",
                    url=url,
                )
            ]

    @classmethod
    def from_error(cls, type: str, msg: str):
        """
        Create one :class:`DetailItem` from error message.
        """
        return cls(
            title=f"❗ {type}",
            subtitle=f"💬 {msg}",
        )


@dataclasses.dataclass
class InfoItem(ArsBaseItem):
    """
    Represent an item to show any information. Nothing would happen when user
    press any of the user action key.
    """


class OpenUrlItem(ArsBaseItem):
    """
    Represent an item to open a url when user tap "Enter".
    """

    def enter_handler(self, ui: "zf.UI"):  # pragma: no cover
        self.open_url_or_print(ui, self.arg)


@dataclasses.dataclass
class OpenFileItem(ArsBaseItem):
    """
    Represent an item to open a file when user tap "Enter".
    """

    def enter_handler(self, ui: "zf.UI"):  # pragma: no cover
        zf.open_file(Path(self.arg))

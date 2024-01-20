# -*- coding: utf-8 -*-

"""
See :class:`ResourceDocument`.
"""

import typing as T
import uuid
import json
import dataclasses
from datetime import datetime, timezone

import jmespath
import sayt.api as sayt

try:
    import pyperclip
except ImportError:  # pragma: no cover
    pass

from ..terminal import SUBTITLE, SHORT_SUBTITLE
from .base_document import BaseArsDocument

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
    import aws_console_url.api as acu

    from ..ars_def import ARS
    from ..downloader import T_RESULT_DATA, ResourceIterproxy
    from ..items.api import T_ARS_ITEM


def get_utc_now() -> datetime:
    """
    Get timezone aware datetime object of current time in UTC.
    """
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def to_human_readable_elapsed(sec: int) -> str:
    """
    Convert seconds to human-readable string.

    Example:

        >>> to_human_readable_elapsed(1)
        "1 sec"
        >>> to_human_readable_elapsed(320)
        "5 min 20 sec"
        >>> to_human_readable_elapsed(4200)
        "1 hour 10 min"
        >>> to_human_readable_elapsed(100000)
        "1 day 3.7 hours"
    """
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


def to_utc_dt(dt: datetime) -> datetime:
    """
    Convert to timezone aware datetime object in UTC.

    If the input datetime object doesn't have timezone, it will assume it's in UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    else:
        return dt.astimezone(timezone.utc)


SIMPLE_DT_FMT = "%Y-%m-%d %H:%M:%S"


def to_simple_dt_fmt(dt: datetime) -> str:
    """
    To simple datetime format string.
    """
    return dt.strftime(SIMPLE_DT_FMT)


def to_iso_dt_fmt(dt: datetime) -> str:
    """
    To ISO datetime format string.
    """
    return dt.isoformat()


def get_none_or_default(
    data: "T_RESULT_DATA",
    path: str,
    default: T.Optional[T.Any] = None,
) -> T.Optional[T.Any]:
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

    :param data: The data to get value from. It represent an AWS resource
        in the boto3 API response. Usually it can be a dictionary or a string.
    :param path: jmespath syntax
    :param default: default value if the value doesn't exist
    """
    value = jmespath.search(path, data)
    return default if value is None else value


def get_description(
    data: "T_RESULT_DATA",
    path: str,
    default: T.Optional[str] = "No description",
) -> str:
    desc = get_none_or_default(data, path)
    if desc:
        return desc
    else:
        return default


def get_datetime(
    data: "T_RESULT_DATA",
    path: str,
    default: T.Optional[datetime] = datetime(1970, 1, 1, tzinfo=timezone.utc),
    as_utc: bool = True,
) -> T.Optional[datetime]:
    """
    Extract timezone aware datetime object from ``data`` using Jmespath.

    Example:

        >>> get_datetime({"CreateDate": datetime(2021, 1, 1)}, path="CreateDate")
        datetime(2021, 1, 1)
    """
    dt = get_none_or_default(data, path, default)
    if dt is None:
        return dt

    if as_utc:
        return to_utc_dt(dt)
    else:
        return dt


def get_datetime_simple_fmt(
    data: "T_RESULT_DATA",
    path: str,
    default: str = "No datetime",
    as_utc: bool = True,
) -> str:
    """
    Extract isoformat datetime string from a dictionary using Jmespath.

    Example:

        >>> get_datetime_simple_fmt({"CreateDate": datetime(2021, 1, 1, microsecond=123000)}, path="CreateDate")
        "2021-01-01 00:00:00"
    """
    dt = get_datetime(data, path, default=None, as_utc=as_utc)
    if dt is None:
        return default
    else:
        return to_simple_dt_fmt(dt)


def get_datetime_iso_fmt(
    data: "T_RESULT_DATA",
    path: str,
    default: str = "No datetime",
    as_utc: bool = True,
) -> str:
    """
    Extract isoformat datetime string from a dictionary using Jmespath.

    Example:

        >>> get_datetime_iso_fmt({"CreateDate": datetime(2021, 1, 1)}, path="CreateDate")
        "2021-01-01T00:00:00"
    """
    dt = get_datetime(data, path, default=None, as_utc=as_utc)
    if dt is None:
        return default
    else:
        return to_iso_dt_fmt(dt)


@dataclasses.dataclass
class ResourceDocument(BaseArsDocument):
    """
    This is the base class for searchable AWS resource document for all
    AWS resource type. Also, it provides some utility functions to help with
    writing the concrete document class for a specific AWS resource type.

    A 'document' is a searchable object stored in the index, representing
    the detailed data of an AWS resource.

    In the ``aws_resource_search.res.${service}.py`` module, we need to inherit
    this class to create a document class for each AWS resource type. For example,
    you can define a document class for S3 bucket like this:

        >>> @dataclasses.dataclass
        >>> class S3BucketDocument(ResourceDocument):
        ...    pass

    :param raw_data: The raw data from the boto3 API call response.
        For example, for
        `s3_client.list_buckets <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_buckets.html>`,
        the raw data is
        ``{'Name': 'string', 'CreationDate': datetime(2015, 1, 1)}``
    :param id: the unique id of the aws resource, most of the time it's the
        same as the resource name. For example, AWS Lambda function name,
        S3 bucket name. But for some resources, it's not. For example,
        AWS EC2 instance id, AWS VPC id. This field is also used as a searchable
        ``IdField`` in :class:`aws_resource_search.base_searcher.BaseSearcher`.
    :param name: the human friendly name of the aws resource. For example,
        AWS Lambda function name, S3 bucket name. This field is also used as a
        searchable ``NgramWordsField`` in :class:`aws_resource_search.base_searcher.BaseSearcher`.
    :param name: similar to name, but this field is used as a searchable
        ``TextField`` in :class:`aws_resource_search.base_searcher.BaseSearcher`.

    In your subclass, you must implement the following methods.
    Please read the docstrings to understand their functionality.

    - :meth:`from_resource`
    - :meth:`title`
    - :meth:`arn`
    - :meth:`get_console_url`

    **Subclass FAQ**

    - Q: I see there's an attribute in the raw data from the boto3 API response,
        should I create a ``dataclasses.field()`` for it?
    - A: Depends. If you want it to be searchable, yes, declare a field for it.
        If you don't want it to be searchable, and you just want to reference
        it later, declare a ``@property`` attribute instead.

    - Q: I have a derivable attribute can be calculated from the raw data,
        should I create a ``dataclasses.field()`` for it?
    - A: Depends.
        1. if you want it to be searchable, yes, declare a field for it.
        2. if the value can be calculated only using the raw data,
            declare a ``@property`` attribute instead.
        3. if the calculation needs additional information like the
            ``BotoSesManager`` object you used for the boto3 API call,
            then you need to create a ``dataclasses.field()`` for it.
            Because you can't calculate it again when getting it back
            from the search index. At that time, you don't have access
            to the original ``BotoSesManager`` object.
    """

    # fmt: off
    raw_data: "T_RESULT_DATA" = dataclasses.field(metadata={"field": sayt.StoredField(name="raw_data")})
    id: str = dataclasses.field(metadata={"field": sayt.IdField(name="id", field_boost=5.0, stored=True)})
    name: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True, sortable=True, ascending=True)})
    name_text: str = dataclasses.field(metadata={
        "field": sayt.TextField(name="name_text", stored=False, sortable=True, ascending=True)}, init=False)
    # fmt: on

    def __post_init__(self):
        name_text = self.name
        for char in "-_":
            name_text = name_text.replace(char, " ")
        self.name_text = name_text

    @classmethod
    def from_resource(
        cls,
        resource: "T_RESULT_DATA",
        bsm: "BotoSesManager",
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

        Then, the implementation should be::

            >>> @dataclasses.dataclass
            ... class S3BucketDocument(ResourceDocument):
            ...     @classmethod
            ...     def from_resource(
            ...         cls,
            ...         resource: "T_RESULT_DATA",
            ...         bsm: "BotoSesManager",
            ...         boto_kwargs: dict,
            ...     ):
            ...         return cls(
            ...             raw_data=resource,
            ...             id=resource["Name"],
            ...             name=resource["Name"],
            ...         )

        .. note::

            You have to implement this method for each AWS Resource Type.
        """
        raise NotImplementedError

    @classmethod
    def from_many_resources(
        cls,
        resources: "ResourceIterproxy",
        bsm: "BotoSesManager",
        boto_kwargs: dict,
    ):
        """
        A wrapper of :meth:`~ResourceDocument.from_resource` to create a list of
        document objects.
        """
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
            ... class S3BucketDocument(ResourceDocument):
            ...     @property
            ...     def title(self) -> str:
            ...         return f"bucket name = {self.name}"

        .. important::

            You have to implement this method for each AWS Resource Type.
        """
        raise NotImplementedError

    @property
    def subtitle(self) -> str:
        """
        The subtitle in the zelfred UI.

        .. seealso::

            :const:`~aws_resource_search.terminal.SUBTITLE`
        """
        return SUBTITLE

    @property
    def short_subtitle(self) -> str:
        """
        A shorter version of subtitle.

        .. seealso::

            :const:`~aws_resource_search.terminal.SHORT_SUBTITLE`
        """
        return SHORT_SUBTITLE

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

        If the ``raw_data`` does not sufficient information to construct the ARN,
        you should declare a ``dataclasses.field()`` for it and initialize it
        in the :meth:`~ResourceDocument.from_resource` method. Then you can just
        reference it here.

        .. important::

            You have to implement this method for each AWS Resource Type.
        """
        msg = f"{self.__class__.__name__} doesn't support ARN"
        raise NotImplementedError(msg)

    def get_console_url(self, console: "acu.AWSConsole") -> str:
        """
        AWS Console URL to view this AWS resource in the console.
        If applicable, User can tap 'Enter' to open in browser.

        .. important::

            You have to implement this method for each AWS Resource Type.
        """
        msg = f"{self.__class__.__name__} doesn't support AWS Console url"
        raise NotImplementedError(msg)

    @classmethod
    def get_list_resources_console_url(cls, console: "acu.AWSConsole") -> str:
        """
        AWS Console URL to view list all AWS resources of this type in the console.
        If applicable, User can tap 'Enter' to open in browser.

        .. important::

            You have to implement this method for each AWS Resource Type.
        """
        msg = f"{cls.__name__} doesn't support list resources AWS Console url"
        raise NotImplementedError(msg)

    @staticmethod
    def one_line(obj, na: str = "NA") -> str:
        """
        Convert a python object to one line json string.

        This is usually used in the :meth:`ResourceDocument.get_details`` method
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

    def get_details(self, ars: "ARS") -> T.List["T_ARS_ITEM"]:
        """
        Call boto3 API to get additional details for this resource. The detailed
        information will be rendered in the dropdown menu. It allows user to tap
        'Ctrl + P' to enter a sub-session to view the details. User can tap
        'F1' to go back to the previous session.

        .. important::

            You have to implement this method for each AWS Resource Type.

        .. note::

            Here's some tips to implement this method correctly:

            1. For immutable attributes, such as resource id, name, you can
                extract them from the ``raw_data``. For example, the Ec2 instance id.
            2. For mutable attributes, such as tags, you have to call boto3 API,
                because the ``raw_data`` is from the index and could be outdated.
            3. Use :meth:`~ResourceDocument.enrich_details` context manager when you
                need to call boto3 API. Because it may fail due to permission issue,
                or resource not exists issue.
        """
        msg = f"{self.__class__.__name__} doesn't support get details"
        raise NotImplementedError(msg)

    @classmethod
    def get_dataset_fields(
        cls,
        id_field_boost: float = 5.0,
        name_minsize: int = 2,
        name_maxsize: int = 4,
        name_sortable: bool = True,
        name_ascending: bool = True,
    ) -> T.List[sayt.T_Field]:
        """
        A helper function to generate the arguments for
        :attr:`Searcher.fields` property.

        By default, it will generate three fields:

        - ``raw_data`` (``StoredField``), to store the raw data from boto3 API response.
        - ``id`` (``IdField``), this field should have higher weight (in id_field_boost).
        - ``name`` (``NgramWordsField``), the default setting is that the result
            is ordered by name in ascending order (in name_sortable and name_ascending).

        Also, for each ``dataclasses.field`` you declared, it will use the
        search field declaration stored in
        ``dataclasses.field(..., metadata={"field": sayt.SomeField(name=...)})``.
        This method performs basic validation on the field declaration.
        This method helps your AWS resource document data model and search index
        schema in sync and avoid human-mistake.

        :param id_field_boost: parameter for the id field.
        :param name_minsize: parameter for the name fields.
        :param name_maxsize: parameter for the name fields.
        :param name_sortable: parameter for the name fields.
        :param name_ascending: parameter for the name fields.
        """
        # search_fields = [
        #     sayt.StoredField(name="raw_data"),
        #     sayt.IdField(name="id", field_boost=id_field_boost, stored=True),
        #     sayt.NgramWordsField(
        #         name="name",
        #         minsize=name_minsize,
        #         maxsize=name_maxsize,
        #         stored=True,
        #         sortable=name_sortable,
        #         ascending=name_ascending,
        #     ),
        # ]
        # _set = {"raw_data", "id", "name"}
        search_field_mapper = {}
        for field in dataclasses.fields(cls):
            try:
                search_field = field.metadata["field"]
            except KeyError:
                raise KeyError(
                    "you forget to define "
                    '``dataclasses.field(..., metadata={"field": sayt.SomeField(name="...")})`` '
                    f"for ``{cls.__name__}.{field.name}`` field"
                )

            if not isinstance(search_field, sayt.BaseField):
                raise TypeError(
                    f"the search field in ``{cls.__name__}.{field.name}`` "
                    f"is not a ``sayt.BaseField`` instance"
                )

            if search_field.name != field.name:
                raise ValueError(
                    f"dataclass field name {field.name!r} doesn't match "
                    f"search field name {search_field.name!r}"
                )
            search_field_mapper[search_field.name] = search_field

        search_field_mapper["id"] = dataclasses.replace(
            search_field_mapper["id"],
            field_boost=id_field_boost,
        )
        search_field_mapper["name"] = dataclasses.replace(
            search_field_mapper["name"],
            minsize=name_minsize,
            maxsize=name_maxsize,
            sortable=name_sortable,
            ascending=name_ascending,
        )
        return list(search_field_mapper.values())


T_ARS_RESOURCE_DOCUMENT = T.TypeVar("T_ARS_RESOURCE_DOCUMENT", bound=ResourceDocument)

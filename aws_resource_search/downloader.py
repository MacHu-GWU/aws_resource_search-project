# -*- coding: utf-8 -*-

"""
This module provides utilities to download AWS resource data from AWS API.
"""

import typing as T
import dataclasses

import jmespath
from iterproxy import IterProxy

from .base_model import BaseModel

if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager
    import sayt.api as sayt

T_RESULT_DATA = T.Union["sayt.T_DOCUMENT", str]
"""
Type hint for boto3 API result data. Each one represents a single AWS resource.
"""


class ResourceIterproxy(IterProxy[T_RESULT_DATA]):
    """
    Advanced iterator object for AWS resource data in boto3 API response.

    Ref: https://github.com/MacHu-GWU/iterproxy-project
    """


@dataclasses.dataclass
class ResultPath(BaseModel):
    """
    Defines how to extract list of AWS resource data from boto3 API call response.

    For example, the
    `s3_client.list_buckets <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_buckets.html>`_
    API call returns the following response:

    .. code-block:: python

        {
            'Buckets': [
                {
                    'Name': 'string',
                    'CreationDate': datetime(2015, 1, 1)
                },
            ],
            'Owner': {
                'DisplayName': 'string',
                'ID': 'string'
            }
        }

    We aim to extract the list of S3 bucket data from the ``Buckets`` field
    of the response. Similarly, for EC2 Instance, the result path for
    ``ec2_client.describe_instances <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html>`_
    API call response is ``Reservations[].Instances[]``.

    :param path: the `jmespath <https://jmespath.org/>`_ notation to the result path.
        It will return an empty list if the result path doesn't exist in the response.
    :param _compiled: the compiled jmespath expression. This class will be created
        only once for each AWS resource type, so that we should cache it for
        better performance.
    """

    path: str = dataclasses.field()
    _compiled: jmespath.parser.ParsedResult = dataclasses.field(init=False)

    def __post_init__(self):
        self._compiled = jmespath.compile(self.path + " || `[]`")

    def extract(self, response: dict) -> T.Iterator[T_RESULT_DATA]:
        """
        Extract list of AWS resource data from boto3 API call response.

        :param response: original boto3 API response

        :return: for example, for ``s3_client.list_buckets``, it will return:

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
    bsm: "BotoSesManager",
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

    :param bsm: the ``boto_session_manager.BotoSesManager`` object.
    :param service: the AWS service name for creating the boto3 client.
        for example, the AWS S3 service name is ``s3``.
    :param method: the boto3 client API method to call for listing AWS resources.
        for example, we use ``list_buckets`` method for getting AWS S3 buckets,
        we use ``describe_instances`` method for getting AWS EC2 instances.
    :param is_paginator: boolean value to indicate whether the method is a paginator.
        for example, it is False for ``s3.list_buckets`` method,
        it is True for ``ec2.describe_instances`` method.
    :param boto_kwargs: the keyword arguments for the boto3 client API call.
        if it is a paginator, it often contains ``PaginationConfig`` key.
    :param result_path: the :class:`ResultPath` object to extract list of AWS resource
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


def extract_tags(data: dict) -> T.Dict[str, str]:
    """
    Extract tags key value pair from boto3 API call response data.

    :param data: it is the dictionary representation of one AWS resource,
        it could be the original boto3 API response, it also could be
        a nested dictionary. For example: in ``s3.list_buckets`` response,
        the original response is the data, because it has a ``TagSet`` field.
        in ``iam.list_roles`` response, the dict in the ``Roles`` list is the data.
    """
    if "tags" in data:
        tag_data = data["tags"]
    elif "Tags" in data:
        tag_data = data["Tags"]
    elif "TagSet" in data:
        tag_data = data["TagSet"]
    elif "TagList" in data:
        tag_data = data["TagList"]
    else:
        return {}

    if isinstance(tag_data, dict):
        return tag_data
    elif isinstance(tag_data, list):
        tags = {}
        for dct in tag_data:
            if "Key" in dct:
                tags[dct["Key"]] = dct["Value"]
            elif "key" in dct:
                tags[dct["key"]] = dct["value"]
            elif "TagKey" in dct:
                tags[dct["TagKey"]] = dct["TagValue"]
            else:
                raise ValueError(f"unable to extract tags from {data}")
        return tags
    else:
        raise TypeError(f"unable to extract tags from {data}")

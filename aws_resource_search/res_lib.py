# -*- coding: utf-8 -*-

"""
Utility class and function in this module will be used in
:mod:`aws_resource_search.res` module.
"""

import typing as T
import dataclasses

import jmespath
import sayt.api as sayt
from iterproxy import IterProxy
from boto_session_manager import BotoSesManager

from .model import BaseModel


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
            kwargs = {}
        client = bsm.get_client(service)
        if is_paginator:
            paginator = client.get_paginator(method)
            for response in paginator.paginate(**kwargs):
                yield from result_path.extract(response)
        else:
            response = getattr(client, method)(**kwargs)
            yield from result_path.extract(response)

    return ResourceIterproxy(func())

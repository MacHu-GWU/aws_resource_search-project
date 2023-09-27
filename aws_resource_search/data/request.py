# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import jmespath
from iterproxy import IterProxy

from ..constants import (
    AWS_ACCOUNT_ID,
    AWS_REGION,
    _ITEM,
    _RESULT,
)
from .common import BaseModel, NOTHING
from .types import T_RESULT_ITEM
from .token import evaluate_token


if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager


class ResultItemIterproxy(IterProxy[T_RESULT_ITEM]):
    pass


@dataclasses.dataclass
class Attribute(BaseModel):
    """
    代表了 :attr:`Request.result` 中的一个属性. 这个属性是一个可以被 evaluate 的
    :class:`aws_resource_search.data.token.BaseToken`.

    """

    type: str = dataclasses.field()
    value: T.Any = dataclasses.field()

    def evaluate(
        self,
        item: T.Dict[str, T.Any],
        context: T.Optional[T.Dict[str, T.Any]] = None,
    ):
        return evaluate_token(self.value, item, context)


@dataclasses.dataclass
class Request(BaseModel):
    """
    代表了一个用来列出许多 AWS 资源的请求. 例如列出所有 S3 Bucket, 列出所有 EC2 Instance 等等.

    :param client: 用户从 boto session 获取底层 client 的, 例如: ``boto3.client("${client}")``
    :param method: 底层 client 所需要调用的方法名, 例如对于列出 S3 Bucket 就要用到 ``list_buckets``,
        对于列出 EC2 Instance 就要用到 ``describe_instances``.
    :param kwargs: 底层 client 所需要调用的方法的参数, 例如对于列出 S3 Bucket 就不需要参数,
        对于列出 EC2 Instance 可能需要 ``Filters`` 参数, 如果用的是 Paginator 则还需要
        ``PaginationConfig`` 参数.
    :param is_paginator: 表示这个 API 是否是用的 paginator, 如果是的话, 我们调用 API 的
        逻辑会略有不同.
    :param items_path: 用来从 Response 中获取代表着很多 AWS 资源的列表的 jmespath 表达式.
        例如对于 ``s3_client.list_buckets`` 来说就是 ``$Buckets``, 而对于
        ``ec2_client.describe_instances`` 来说就是 ``$Reservations[].Instances[]``.
    :param result: 用 jmespath 表达式来描述如何从 Response 中获取到我们想要的结果. 例如
        筛选部分字段, 重命名字段, 或者用 :class:`~aws_resource_search.data.token.Token`
        来获取更复杂的结果.

    **Usage Example**

    举例来说, 我们想用
    `s3_client.list_buckets <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_buckets.html>`_
    API 来列出 S3 Bucket. 通过查文档我们知道这个 API 不是 paginator, 它的 response 长这样::

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

    那么这个 request 就可以这么写::

        >>> request = Request(
        ...     client="s3",
        ...     method="list_buckets",
        ...     is_paginator=False,
        ...     # how to locate list of bucket details in the response object
        ...     items_path="$Buckets",
        ...     result={ ## extract additional fields
        ...         "bucket": Attribute.from_dict({"type": "str", "value": "$Name"}),
        ...         "arn": Attribute.from_dict({
        ...             "type": "str",
        ...             "value": {
        ...                 "type": "sub",
        ...                 "kwargs": {
        ...                     "template": "arn:aws:s3:::{bucket}",
        ...                     "params": {"bucket": "$Name"},
        ...                 },
        ...             },
        ...         }),
        ...     },
        ... )
        >>> bsm = BotoSesManager(profile_name="my_aws_profile")
        >>> for item in request.invoke(bsm):
        ...     print(item)
        {
            'bucket': 'my-bucket-1',
            'arn': 'arn:aws:s3:::my-bucket-1',
            '_item': {
                'Name': 'my-bucket-1',
                'CreateDate': datetime(2020, 1, 1),
            }
        }
        {
            'bucket': 'my-bucket-2',
            'arn': 'arn:aws:s3:::my-bucket-2',
            '_item': {
                'Name': 'my-bucket-2',
                'CreateDate': datetime(2020, 1, 1),
            }
        }
        ...

    这里的逻辑翻译成人类语言就是, 使用 ``boto3.client("s3").list_buckets()`` API,
    参数是空的, 然后从 response 中的 ``$Buckets`` jmespath 的位置这个列表, 然后对于列表中
    的每一个字典, 我们需要将 ``$Name`` 字段取值, 重命名为 ``bucket`` 字段, 然后再用
    String Template 构建一个 Arn, 其中 template 是 ``arn:aws:s3:::{bucket}``,
    参数 params 是 ``{"bucket": "$Name"}``. 参数中的 bucket 也是通过 jmespath 从
    原字典中提取的.
    """

    client: str = dataclasses.field(default=NOTHING)
    method: str = dataclasses.field(default=NOTHING)
    kwargs: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)
    is_paginator: bool = dataclasses.field(default=NOTHING)
    items_path: str = dataclasses.field(default=NOTHING)
    result: T.Dict[str, Attribute] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, dct: T.Dict[str, T.Any]):
        dct["result"] = {
            key: Attribute.from_dict(value)
            for key, value in dct.get("result", dict()).items()
        }
        return cls(**dct)

    def _select_result(
        self,
        item: T_RESULT_ITEM,
        context: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> T_RESULT_ITEM:
        result = {_ITEM: item, _RESULT: {}}
        if self.result is None:
            return result
        for key, attribute in self.result.items():
            result[_RESULT][key] = attribute.evaluate(item, context)
        return result

    def _invoke(
        self,
        bsm: "BotoSesManager",
        boto_kwargs: T.Optional[dict] = None,
    ) -> T.Iterator[T_RESULT_ITEM]:
        context = {
            AWS_ACCOUNT_ID: bsm.aws_account_id,
            AWS_REGION: bsm.aws_region,
        }
        boto_client = bsm.get_client(self.client)
        if boto_kwargs is not None:
            kwargs = boto_kwargs
        else:
            kwargs = self.kwargs
        if self.is_paginator:
            paginator = boto_client.get_paginator(self.method)
            expr = jmespath.compile(self.items_path[1:])
            for response in paginator.paginate(**kwargs):
                for item in expr.search(response):
                    yield self._select_result(item, context)
        else:
            method = getattr(boto_client, self.method)
            response = method(**kwargs)
            expr = jmespath.compile(self.items_path[1:])
            for item in expr.search(response):
                yield self._select_result(item, context)

    def invoke(
        self,
        bsm: "BotoSesManager",
        boto_kwargs: T.Optional[dict] = None,
    ) -> ResultItemIterproxy:
        """
        todo: add docstring
        """
        return ResultItemIterproxy(self._invoke(bsm, boto_kwargs))

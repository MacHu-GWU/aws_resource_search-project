# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from ..constants import (
    _RES,
    _CTX,
    _OUT,
)
from .common import BaseModel
from .types import T_RESOURCE, T_EVAL_DATA, T_OUTPUT
from .token import evaluate_token


@dataclasses.dataclass
class Attribute(BaseModel):
    """
    代表了 output 中的一个属性. 这个属性是一个可以被 evaluate 的
    :class:`aws_resource_search.data.token.BaseToken`.

    Example:

        >>> attr = Attribute(type="str", token="$Name")
        >>> attr.evaluate({"Name": "alice"})
        'alice'
    """

    type: str = dataclasses.field()
    token: T.Any = dataclasses.field()

    def evaluate(
        self,
        data: T_EVAL_DATA,
    ):
        return evaluate_token(self.token, data)


def extract_output(
    output: T.Dict[str, "Attribute"],
    resource: T_RESOURCE,
    context: T.Optional[T.Dict[str, T.Any]] = None,
) -> T_OUTPUT:
    """
    从 boto3 api 返回的 AWS resource的数据中提取出 output 中定义的属性.

    Example:

        >>> data = extract_output(
        ...     output={
        ...         "arn": Attribute(
        ...             type="str",
        ...             token={
        ...                 "type": "sub",
        ...                 "kwargs": {
        ...                     "template": "arn:aws:s3:{aws_region}:{aws_account_id}:bucket/{bucket}",
        ...                     "params": {
        ...                         "bucket": "$_res.Name",
        ...                         "aws_region": "$_ctx.AWS_REGION",
        ...                         "aws_account_id": "$_ctx.AWS_ACCOUNT_ID",
        ...                     },
        ...                 },
        ...             },
        ...         ),
        ...     },
        ...     resource={
        ...         "Name": "my-bucket",
        ...     },
        ...     context={"AWS_ACCOUNT_ID": "123456789012", "AWS_REGION": "us-east-1"},
        ... )
        >>> data[_OUT]
        {'arn': 'arn:aws:s3:us-east-1:123456789012:bucket/my-bucket'}

    :param output: 一个 key 为属性名, value 为 :class:`Attribute` 的 dict.
    :param res: boto3 api 返回的 AWS resource 的数据. 例如 ``s3_client.list_buckets()``
        返回的就是 ``{"Name": "string", "CreationDate": datetime(2015, 1, 1)}``.
    :param context: 额外的 context 信息, 通常是当前的 aws account id 和 region.
    """
    data = {_RES: resource, _CTX: context, _OUT: {}}
    for key, attribute in output.items():
        data[_OUT][key] = attribute.evaluate(data)
    del data[_CTX]
    return data

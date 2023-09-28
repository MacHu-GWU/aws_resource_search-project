# -*- coding: utf-8 -*-

"""
This module implements the logic to parse ``${service_id}.${resource_type}.doc``
json node, and create the searchable document data using AWS resource data and
 extracted output data.
"""

import typing as T
import dataclasses

import sayt.api as sayt

from ..constants import (
    FieldTypeEnum,
    RAW_DATA,
)
from .types import T_OUTPUT, T_EVAL_DATA
from .common import BaseModel
from .token import evaluate_token


_type_to_field_class_mapper = {
    FieldTypeEnum.Stored.value: sayt.StoredField,
    FieldTypeEnum.Id.value: sayt.IdField,
    FieldTypeEnum.IdList.value: sayt.IdListField,
    FieldTypeEnum.Keyword.value: sayt.KeywordField,
    FieldTypeEnum.Text.value: sayt.TextField,
    FieldTypeEnum.Numeric.value: sayt.NumericField,
    FieldTypeEnum.Datetime.value: sayt.DatetimeField,
    FieldTypeEnum.Boolean.value: sayt.BooleanField,
    FieldTypeEnum.Ngram.value: sayt.NgramField,
    FieldTypeEnum.NgramWords.value: sayt.NgramWordsField,
}


@dataclasses.dataclass
class Field(BaseModel):
    """
    代表了 doc 中一个可以被搜索的字段.

    :param name: 这个字段的名字. 不能以下划线开头.
    :param type: 用于最终生成 ``whoosh.fields.Field`` 的类型. 必须要是
        :class:`aws_resource_search.constants.FieldTypeEnum` 中定义的值.
    :param token: 一个可以被最终 evaluate 的 token.
    :param kwargs: 用于最终生成 ``whoosh.fields.Field`` 的其他参数, 例如 Ngram 就可以
        指定 ``minsize`` 和 ``maxsize``.
    """

    name: str = dataclasses.field()
    type: str = dataclasses.field()
    token: T.Any = dataclasses.field()
    kwargs: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    def evaluate(self, data: T_EVAL_DATA):
        return evaluate_token(self.token, data)

    def _to_sayt_field(self) -> sayt.T_Field:
        field_class = _type_to_field_class_mapper[self.type]
        return field_class(name=self.name, **self.kwargs)


_ = T.Dict[str, Field]


def parse_doc_json_node(
    dct: T.Dict[str, T.Any]
) -> T.Dict[str, "Field"]:  # pragma: no cover
    fields = {k: Field.from_dict(dict(name=k, **v)) for k, v in dct.items()}
    fields[RAW_DATA] = Field(
        name=RAW_DATA,
        type=FieldTypeEnum.Stored.value,
        token=f"$@",
    )
    return fields


def extract_document(
    document: T.Dict[str, Field],
    output: T_OUTPUT,
) -> T.Dict[str, T.Any]:
    """
    Example:

        >>> extract_document(
        ...     document={
        ...         "id": Field(
        ...             name="id",
        ...             type="Id",
        ...             token="$_res.instance_id",
        ...         ),
        ...     }
        ...     output={"_res": {"instance_id": "i-1a2b"}, "_out": {}},
        ... )
        {
            "id": "i-1a2b",
            'raw_data': {'_res': {'instance_id': 'i-1a2b'}, '_out': {}},
        }
    """
    return {key: field.evaluate(output) for key, field in document.items()}

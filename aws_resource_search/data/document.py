# -*- coding: utf-8 -*-

"""
This module implements the logic to parse ``${service_id}.${resource_type}.doc``
json node, and create the searchable document data using AWS resource data and
 extracted output data.
"""

import typing as T
import copy
import dataclasses

import sayt.api as sayt
from aws_console_url.api import AWSConsole

from ..constants import (
    FieldTypeEnum,
    _RES,
    _OUT,
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
    return {k: Field.from_dict(dict(name=k, **v)) for k, v in dct.items()}


def extract_document(
    document: T.Dict[str, Field],
    output: T_OUTPUT,
):
    data = {}
    for key, field in document.items():
        data[key] = field.evaluate(output)
    data[RAW_DATA] = output
    return data
#
#
# a = {
#     "id": "str",
#     "name": "str",
#     "raw_data": {
#         "_res": {},
#         "_out": {},
#     },
# }
#
#
# @dataclasses.dataclass
# class Search(BaseModel):
#     """
#     Defines how to index the result of a :class:`Request`.
#     """
#
#     fields: T.List[Field] = dataclasses.field()
#     url_getter: UrlGetter = dataclasses.field()
#
#     def __post_init__(self):
#         super().__post_init__()
#         self.fields.extend(
#             [
#                 Field(
#                     name=RAW_RES,
#                     type=FieldTypeEnum.Stored.value,
#                     value=f"${_RES}",
#                 ),
#                 Field(
#                     name=RAW_RESULT,
#                     type=FieldTypeEnum.Stored.value,
#                     value=f"${_OUT}",
#                 ),
#             ]
#         )
#
#     @classmethod
#     def from_dict(cls, dct: dict):
#         dct = copy.deepcopy(dct)
#         fields = []
#         for field in dct.get("fields", []):
#             fields.append(Field(**field))
#         dct["fields"] = fields
#         dct["url_getter"] = UrlGetter(**dct["url_getter"])
#         return cls(**dct)
#
#     def _item_to_doc(
#         self,
#         item: T.Dict[str, T.Any],
#     ) -> T.Dict[str, T.Any]:
#         """
#         Convert the item into a document that can be indexed by whoosh.
#
#
#         Sample item::
#             >>> item ={
#             ...     "${additional_attribute_extracted_by_result_selector}": "...",
#             ...     "arn": "arn:aws:s3:::my-bucket",
#             ...     "_item": {
#             ...         "Bucket": "my-bucket"
#             ...     },
#             ... }
#             >>> fields = [
#             ...     {
#             ...         "name": "id",
#             ...         "type": "Id",
#             ...         "value": "$arn"
#             ...     },
#             ... ]
#             >>> Search(fields=fields)._item_to_doc(item)
#             {
#                 'id': 'arn:aws:s3:::my-bucket',
#                 'raw_item': {
#                     'Bucket': 'my-bucket'
#                 }
#             }
#         """
#         doc = {}
#         for field in self.fields:
#             doc[field.name] = evaluate_token(field.value, item)
#         return doc
#
#     def _doc_to_url(
#         self,
#         doc: T.Dict[str, T.Any],
#         console: AWSConsole,
#     ) -> str:
#         """
#         Get the aws console url from the document data. A document usually has a
#         ``id`` field that can be used as a unique identifier, a human friendly
#         ``name`` field that can be searched by ngram, and a ``raw_item`` field
#         that contains the original item data.
#
#         Sample document::
#
#             {
#                 "id": ...
#                 "name": ...
#                 "console_url": ...
#                 "raw_item": {
#                     ...,
#                     "arn": ...
#                 }
#             }
#         """
#         kwargs = dict()
#         for key, value in self.url_getter.kwargs.items():
#             kwargs[key] = evaluate_token(value, doc)
#         return getattr(
#             getattr(console, self.url_getter.service_id),
#             self.url_getter.method,
#         )(**kwargs)

# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import sayt.api as sayt
from aws_console_url.api import AWSConsole

from ..constants import (
    FieldTypeEnum, _ITEM, _RESULT, RAW_ITEM, RAW_RESULT,
)
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
    value: T.Any = dataclasses.field()
    kwargs: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    def _to_sayt_field(self) -> sayt.T_Field:
        field_class = _type_to_field_class_mapper[self.type]
        return field_class(name=self.name, **self.kwargs)


@dataclasses.dataclass
class UrlGetter(BaseModel):
    service_id: str = dataclasses.field()
    method: str = dataclasses.field()
    kwargs: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class Search(BaseModel):
    """
    Defines how to index the result of a :class:`Request`.
    """

    fields: T.List[Field] = dataclasses.field()
    url_getter: UrlGetter = dataclasses.field()

    def __post_init__(self):
        super().__post_init__()
        self.fields.extend([
            Field(
                name=RAW_ITEM,
                type=FieldTypeEnum.Stored.value,
                value=f"${_ITEM}",
            ),
            Field(
                name=RAW_RESULT,
                type=FieldTypeEnum.Stored.value,
                value=f"${_RESULT}",
            ),
        ])

    @classmethod
    def from_dict(cls, dct: dict):
        fields = []
        for field in dct.get("fields", []):
            fields.append(Field(**field))
        dct["fields"] = fields
        dct["url_getter"] = UrlGetter(**dct["url_getter"])
        return cls(**dct)

    def _item_to_doc(
        self,
        item: T.Dict[str, T.Any],
    ) -> T.Dict[str, T.Any]:
        """
        Convert the item into a document that can be indexed by whoosh.


        Sample item::
            >>> item ={
            ...     "${additional_attribute_extracted_by_result_selector}": "...",
            ...     "arn": "arn:aws:s3:::my-bucket",
            ...     "_item": {
            ...         "Bucket": "my-bucket"
            ...     },
            ... }
            >>> fields = [
            ...     {
            ...         "name": "id",
            ...         "type": "Id",
            ...         "value": "$arn"
            ...     },
            ... ]
            >>> Search(fields=fields)._item_to_doc(item)
            {
                'id': 'arn:aws:s3:::my-bucket',
                'raw_item': {
                    'Bucket': 'my-bucket'
                }
            }
        """
        doc = {}
        for field in self.fields:
            doc[field.name] = evaluate_token(field.value, item)
        return doc

    def _doc_to_url(
        self,
        doc: T.Dict[str, T.Any],
        console: AWSConsole,
    ) -> str:
        """
        Get the aws console url from the document data. A document usually has a
        ``id`` field that can be used as a unique identifier, a human friendly
        ``name`` field that can be searched by ngram, and a ``raw_item`` field
        that contains the original item data.

        Sample document::

            {
                "id": ...
                "name": ...
                "console_url": ...
                "raw_item": {
                    ...,
                    "arn": ...
                }
            }
        """
        kwargs = dict()
        for key, value in self.url_getter.kwargs.items():
            kwargs[key] = evaluate_token(value, doc)
        return getattr(
            getattr(console, self.url_getter.service_id),
            self.url_getter.method,
        )(**kwargs)

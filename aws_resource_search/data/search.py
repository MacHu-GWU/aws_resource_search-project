# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import jmespath
from iterproxy import IterProxy
import sayt.api as sayt

from ..constants import AWS_ACCOUNT_ID, AWS_REGION, FieldTypeEnum
from ..compat import cached_property
from .common import BaseModel, NOTHING
from .types import T_RESULT_ITEM
from .token import token_class_mapper, evaluate_token


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

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(**dct)

    def _to_sayt_field(self) -> sayt.T_Field:
        field_class = _type_to_field_class_mapper[self.type]
        return field_class(name=self.name, **self.kwargs)


@dataclasses.dataclass
class Search(BaseModel):
    """
    Defines how to index the result of a :class:`Request`.
    """

    fields: T.List[Field] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        field = Field(
            name="raw_item",
            type=FieldTypeEnum.Stored.value,
            value="$_item",
        )
        self.fields.append(field)

    @classmethod
    def from_dict(cls, dct: dict):
        fields = []
        for field in dct.get("fields", []):
            fields.append(Field(**field))
        return cls(fields=fields)

    def _item_to_doc(
        self,
        item: T.Dict[str, T.Any],
    ) -> T.Dict[str, T.Any]:
        """
        Convert the item into a document that can be indexed by whoosh.
        """
        doc = {}
        for field in self.fields:
            doc[field.name] = evaluate_token(field.value, item)
        return doc

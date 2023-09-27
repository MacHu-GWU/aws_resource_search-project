# -*- coding: utf-8 -*-

from .vendor.better_enum import BetterStrEnum

CACHE_EXPIRE = 1
LIST_API_CACHE_EXPIRE = 1
FILTER_API_CACHE_EXPIRE = 1

AWS_ACCOUNT_ID = "AWS_ACCOUNT_ID"
AWS_REGION = "AWS_REGION"

_ITEM = "_item"
_RESULT = "_result"
RAW_ITEM = "raw_item"
RAW_RESULT = "raw_result"


class DataTypeEnum(BetterStrEnum):
    str = "str"
    int = "int"
    float = "float"
    bool = "bool"
    datetime = "datetime"
    bytes = "bytes"
    list = "list"
    dict = "dict"
    str_array = "T.List[str]"
    int_array = "T.List[int]"
    kv_dict = "T.Dict[str, T.Any]"


class TokenTypeEnum(BetterStrEnum):
    raw = "raw"
    jmespath = "jmespath"
    sub = "sub"
    join = "join"


class FieldTypeEnum(BetterStrEnum):
    Stored = "Stored"
    Id = "Id"
    IdList = "IdList"
    Keyword = "Keyword"
    Text = "Text"
    Numeric = "Numeric"
    Datetime = "Datetime"
    Boolean = "Boolean"
    Ngram = "Ngram"
    NgramWords = "NgramWords"

# -*- coding: utf-8 -*-

"""
Importable constants value.
"""

from .vendor.better_enum import BetterStrEnum

CACHE_EXPIRE = 1
LIST_API_CACHE_EXPIRE = 1
FILTER_API_CACHE_EXPIRE = 1

AWS_ACCOUNT_ID = "AWS_ACCOUNT_ID"
AWS_REGION = "AWS_REGION"

_RES = "_res"
_CTX = "_ctx"
_OUT = "_out"
RAW_DATA = "raw_data"
CONSOLE_URL = "console_url"

SEP = "____" # separator


class DataTypeEnum(BetterStrEnum):
    """
    List of common data types syntax for type hint.
    """

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


class FieldTypeEnum(BetterStrEnum):
    """
    List of searchable document field types.
    """

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

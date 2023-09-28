# -*- coding: utf-8 -*-

import typing as T

if T.TYPE_CHECKING:  # pragma: no cover
    from .output import Attribute

# key value pair data
T_DATA = T.Dict[str, T.Any]
# the aws resource dictionary or string in list_abx_resource boto3 API response
# for most of the cases, it is a dictionary. occasionally, it is a string
T_RESOURCE = T.Union[T_DATA, str]
# the data that can be evaluated by token
T_EVAL_DATA = T.Optional[T.Union[T_DATA, list, str, int, float, bool]]
# the token that can be evaluated
T_TOKEN = T.Any


class T_OUTPUT(T.TypedDict):
    """
    The data type of the return value of :func:`aws_resource_search.data.output.extract_output`.
    """

    _res: T_RESOURCE
    _out: T_DATA

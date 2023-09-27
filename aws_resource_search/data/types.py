# -*- coding: utf-8 -*-

import typing as T

# the aws resource dictionary or string in list_abx_resource boto3 API response
# for most of the cases, it is a dictionary
T_RESULT_ITEM = T.Dict[str, T.Any]
T_EVAL_DATA = T.Optional[T.Union[T.Dict[str, T.Any], list, str, int, float, bool]]

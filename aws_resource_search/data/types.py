# -*- coding: utf-8 -*-

import typing as T

# the aws resource dictionary or string in list_abx_resource boto3 API response
# for most of the cases, it is a dictionary
T_RESULT_ITEM = T.Dict[str, T.Any]

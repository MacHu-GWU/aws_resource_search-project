# -*- coding: utf-8 -*-

from aws_resource_search.code.searchers import generate_searchers_py_module
from aws_resource_search.code.ars_v2 import generate_ars_v2_py_module

generate_searchers_py_module()
generate_ars_v2_py_module()

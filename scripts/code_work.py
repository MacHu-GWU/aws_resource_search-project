# -*- coding: utf-8 -*-

"""
This script automatically generate the source code based on the update-to-date
resource type list.
"""

from aws_resource_search.code.searchers import generate_searchers_py_module
from aws_resource_search.code.ars import generate_ars_py_module

generate_searchers_py_module()
generate_ars_py_module()

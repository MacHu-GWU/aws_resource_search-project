# -*- coding: utf-8 -*-

"""
This script automatically generate the source code based on the update-to-date
resource type list.
"""

from aws_resource_search.code.searchers import (
    load_raw_searcher_metadata_list,
    sort_searcher_metadata_list,
    dump_raw_searcher_metadata_list,
    enrich_searcher_metadata,
    get_searcher_py_modules,
    generate_searchers_py_module,
    generate_implemented_resource_types,
)
from aws_resource_search.code.ars import generate_ars_py_module

sr_meta_list = load_raw_searcher_metadata_list()
sr_meta_list = sort_searcher_metadata_list(sr_meta_list)
enrich_searcher_metadata(sr_meta_list)

# py_modules = get_searcher_py_modules()
# generate_searchers_py_module(py_modules)
# generate_implemented_resource_types(py_modules)
# generate_ars_py_module()

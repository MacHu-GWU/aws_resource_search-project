# -*- coding: utf-8 -*-

"""
This script automatically generate the source code based on the update-to-date
resource type list.
"""

from aws_resource_search.code.gen_code import (
    load_searchers_enum_json,
    sort_searcher_metadata_list,
    dump_searchers_enum_json,
    generate_searchers_enum_py_module,
    enrich_searcher_metadata,
    dump_searchers_json,
    generate_implemented_resource_types,
    generate_ars_py_module,
)

sr_meta_list = load_searchers_enum_json()
sr_meta_list = sort_searcher_metadata_list(sr_meta_list)
dump_searchers_enum_json(sr_meta_list) # create aws_resource_search/searchers_enum.json
generate_searchers_enum_py_module(sr_meta_list) # create aws_resource_search/searchers_enum.py
enrich_searcher_metadata(sr_meta_list)
dump_searchers_json(sr_meta_list) # create aws_resource_search/searchers.json
generate_implemented_resource_types(sr_meta_list)
generate_ars_py_module(sr_meta_list)

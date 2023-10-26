# -*- coding: utf-8 -*-

import sayt.api as sayt

from .paths import dir_index, dir_cache
from .searchers import searchers_metadata


def downloader():
    return [{"id": resource_type, "name": resource_type} for resource_type in searchers_metadata]


index_name = "aws-resource-search-resource-types"
resource_type_searcher = sayt.DataSet(
    dir_index=dir_index,
    index_name=index_name,
    fields=[
        sayt.IdField(
            name="id",
        ),
        sayt.NgramWordsField(
            name="name",
            stored=True,
            minsize=2,
            maxsize=6,
        ),
    ],
    dir_cache=dir_cache,
    cache_key=index_name,
    cache_tag=index_name,
    cache_expire=24 * 60 * 60,
    downloader=downloader,
)

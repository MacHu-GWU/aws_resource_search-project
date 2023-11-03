# -*- coding: utf-8 -*-

"""
This script helps developer to debug specific AWS resource type searcher.
"""

from rich import print as rprint
from aws_resource_search.ui.boto_ses import bsm, ars


if __name__ == "__main__":
    # --------------------------------------------------------------------------
    query = "*"
    limit = 50
    boto_kwargs = {}
    refresh_data = True
    simple_response = True
    verbose = False
    # --------------------------------------------------------------------------
    sr = ars.s3_bucket
    # sr = ars.iam_role
    # --------------------------------------------------------------------------
    res = sr.search(
        bsm=bsm,
        query=query,
        limit=limit,
        boto_kwargs=boto_kwargs,
        refresh_data=refresh_data,
        verbose=verbose,
    )
    if isinstance(res, dict):
        hits = res.pop("hits")
        docs = [hit["_source"] for hit in hits]
        rprint(res)
    else:
        docs = res

    # for doc in res:
    for doc in res[:3]:
        rprint(doc)
        print(doc.get_console_url(ars.aws_console))

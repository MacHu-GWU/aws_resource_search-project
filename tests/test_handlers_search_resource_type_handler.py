# -*- coding: utf-8 -*-

from aws_resource_search.ui_init import ui
from aws_resource_search.handlers.search_resource_type_handler import (
    search_resource_type_and_return_items,
)


def test_search_resource_type_and_return_items():
    for query in [
        "s3",
        "iam",
        "sfn",
    ]:
        items = search_resource_type_and_return_items(ui=ui, query=query)
        for item in items:
            assert query in item.title


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.handlers.search_resource_type_handler",
        preview=False,
    )

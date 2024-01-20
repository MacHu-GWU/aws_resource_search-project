# -*- coding: utf-8 -*-

import typing as T

import pytest

from aws_resource_search.handlers.search_resource_type_handler import (
    search_resource_type_and_return_items,
)
from aws_resource_search.ui_def import UI
from aws_resource_search.tests.fake_aws.main import FakeAws

# run test that need to hit the index may cause concurrency issue
# we only run this manually on laptop
# @pytest.mark.skip()
class Test(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        cls.setup_ars()
        cls.setup_ui()

    def test_search_resource_type_and_return_items(self):
        for query in [
            "s3",
            "iam",
            "sfn",
        ]:
            items = search_resource_type_and_return_items(ui=self.ui, query=query)
            for item in items:
                assert query in item.title


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.handlers.search_resource_type_handler",
        preview=False,
    )

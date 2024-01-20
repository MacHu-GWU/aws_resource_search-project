# -*- coding: utf-8 -*-

from aws_resource_search.handlers.search_resource_type_handler import (
    search_resource_type_and_return_items,
)
from aws_resource_search.tests.fake_aws.main import FakeAws


class TestSearchResourceTypeHandler(FakeAws):
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

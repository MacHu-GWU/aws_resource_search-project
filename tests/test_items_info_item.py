# -*- coding: utf-8 -*-

from aws_resource_search.items.info_item import InfoItem


class TestInfoItem:
    def test(self):
        _ = InfoItem


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.info_item",
        preview=False,
    )

# -*- coding: utf-8 -*-

from aws_resource_search.items.set_aws_profile_item import SetAwsProfileItem


class TestSetAwsProfileItem:
    def test_from_profile_region(self):
        items = SetAwsProfileItem.from_many_profile_region_pairs(
            [("my_profile", "us-east-1")],
            autocomplete="",
        )
        # print(items)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.set_aws_profile_item",
        preview=False,
    )

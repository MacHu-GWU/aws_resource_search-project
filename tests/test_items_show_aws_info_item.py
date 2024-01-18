# -*- coding: utf-8 -*-

from aws_resource_search.items.show_aws_info_item import ShowAwsInfoItem


class TestShowAwsInfoItem:
    def test_from_path(self):
        item = ShowAwsInfoItem.from_key_value("aws_account_id", "123456789012", autocomplete="")
        print(item)
        # assert str(item.variables["url"]) == "https://www.google.com"
        # ------------------------------------------------------------------
        # We only test this action manually on developer's machine, not in CI.
        # ------------------------------------------------------------------
        # item.enter_handler(ui=None)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.show_aws_info_item",
        preview=False,
    )

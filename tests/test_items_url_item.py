# -*- coding: utf-8 -*-

from aws_resource_search.items.url_item import UrlItem


class TestFileItem:
    def test_from_path(self):
        item = UrlItem.from_url(url="https://www.google.com", uid="uid")
        assert str(item.variables["url"]) == "https://www.google.com"
        # ------------------------------------------------------------------
        # We only test this action manually on developer's machine, not in CI.
        # ------------------------------------------------------------------
        # item.enter_handler(ui=None)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.url_item",
        preview=False,
    )

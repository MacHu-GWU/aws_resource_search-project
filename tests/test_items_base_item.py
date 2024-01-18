# -*- coding: utf-8 -*-

import zelfred.api as zelfred
from aws_resource_search.items.base_item import BaseArsItem


class TestBaseArsItem:
    def test(self):
        url = "https://www.google.com"
        text = "a1b2c3"
        ui = zelfred.UI(handler=lambda x: x)

        item = BaseArsItem(title="hello")
        # ----------------------------------------------------------------------
        # We only test these two action manually on developer's machine, not in CI.
        # ----------------------------------------------------------------------
        # item.open_url_or_print(ui=ui, url=url)
        # item.copy_or_print(ui=ui, text=text)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.base_item",
        preview=False,
    )

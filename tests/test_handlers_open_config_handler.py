# -*- coding: utf-8 -*-

from aws_resource_search.items.file_item import FileItem
from aws_resource_search.handlers.open_config_handler import (
    open_config_handler,
)
from aws_resource_search.tests.fake_aws.main import FakeAws


class Test(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        cls.setup_ars()
        cls.setup_ui()

    def test_open_config_handler(self):
        """
        We don't test handler.
        """
        items = open_config_handler(ui=self.ui, line_input="")
        assert len(items) == 1
        assert isinstance(items[0], FileItem)

        # ------------------------------------------------------------------
        # We only test this action manually on developer's machine, not in CI.
        # ------------------------------------------------------------------
        # items[0].enter_handler(ui=self.ui)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.handlers.open_config_handler",
        preview=False,
    )

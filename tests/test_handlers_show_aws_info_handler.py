# -*- coding: utf-8 -*-

from aws_resource_search.items.show_aws_info_item import ShowAwsInfoItem
from aws_resource_search.handlers.show_aws_info_handler import (
    show_aws_info_handler,
)
from aws_resource_search.tests.fake_aws.main import FakeAws


class TestShowAwsInfoHandler(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        cls.setup_ars()
        cls.setup_ui()

    def test_show_aws_info_handler(self):
        """
        We don't test handler.
        """
        items = show_aws_info_handler(ui=self.ui, line_input="")


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.handlers.show_aws_info_handler",
        preview=False,
    )

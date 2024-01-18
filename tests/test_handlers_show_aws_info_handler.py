# -*- coding: utf-8 -*-

from aws_resource_search.handlers.show_aws_info_handler import (
    show_aws_info_handler,
)


def test_show_aws_info_handler():
    """
    We don't test handler.
    """
    _ = show_aws_info_handler


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.handlers.show_aws_info_handler",
        preview=False,
    )

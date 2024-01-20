# -*- coding: utf-8 -*-

from aws_resource_search.handlers.search_aws_profile_handler import (
    search_aws_profile_and_return_items,
)
from aws_resource_search.tests.mock_aws_cli import test_home_aws_folder


def test_search_aws_profile_handler():
    with test_home_aws_folder.temp():
        items = search_aws_profile_and_return_items(
            line_input="s3-bucket: my-bucket",
            profile_query="*",
            refresh_data=True,
        )
        assert len(items) == 3

        items = search_aws_profile_and_return_items(
            line_input="s3-bucket: my-bucket",
            profile_query="*",
        )
        assert len(items) == 3

        items = search_aws_profile_and_return_items(
            line_input="s3-bucket: my-bucket",
            profile_query="invalidprofile",
        )
        assert len(items) == 1


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.handlers.search_aws_profile_handler",
        preview=False,
    )

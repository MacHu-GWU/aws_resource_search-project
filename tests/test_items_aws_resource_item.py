# -*- coding: utf-8 -*-

from aws_resource_search.res.s3 import S3Bucket
from aws_resource_search.items.aws_resource_item import AwsResourceItem


class TestAwsResourceItem:
    def test_from_many_document(self):
        item = AwsResourceItem.from_many_document(
            resource_type="s3-bucket",
            docs=[
                S3Bucket(
                    id="my-bucket",
                    name="my-bucket",
                    raw_data={},
                ),
            ],
        )[0]
        _ = item.get_id()
        _ = item.get_name()
        _ = item.get_arn()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.aws_resource_item",
        preview=False,
    )

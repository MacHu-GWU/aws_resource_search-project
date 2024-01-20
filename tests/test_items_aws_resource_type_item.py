# -*- coding: utf-8 -*-

from aws_resource_search.documents.resource_type_document import ResourceTypeDocument
from aws_resource_search.items.aws_resource_type_item import AwsResourceTypeItem


class TestAwsResourceTypeItem:
    def test_from_many_document(self):
        from aws_resource_search.ars_init import ars

        item = AwsResourceTypeItem.from_many_document(
            docs=[
                ResourceTypeDocument(
                    id="s3-bucket",
                    name="s3-bucket",
                    desc="s3-bucket",
                    ngram="s3-bucket",
                ),
            ],
            ars=ars,
        )[0]
        assert isinstance(item, AwsResourceTypeItem)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.aws_resource_type_item",
        preview=False,
    )

# -*- coding: utf-8 -*-

from aws_resource_search.documents.resource_type_document import ResourceTypeDocument
from aws_resource_search.items.aws_resource_type_item import AwsResourceTypeItem
from aws_resource_search.tests.fake_aws.api import FakeAws


class TestAwsResourceTypeItem(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        cls.setup_ars()

    def test_from_many_document(self):
        item = AwsResourceTypeItem.from_many_document(
            docs=[
                ResourceTypeDocument(
                    id="s3-bucket",
                    name="s3-bucket",
                    desc="s3-bucket",
                    ngram="s3-bucket",
                ),
            ],
            ars=self.ars,
        )[0]
        assert isinstance(item, AwsResourceTypeItem)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.aws_resource_type_item",
        preview=False,
    )

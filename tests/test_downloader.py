# -*- coding: utf-8 -*-

import pytest
import moto

from aws_resource_search.downloader import (
    T_RESULT_DATA,
    ResourceIterproxy,
    ResultPath,
    list_resources,
    extract_tags,
)
from aws_resource_search.tests.mock_test import BaseMockTest


class Test(BaseMockTest):
    mock_list = [
        moto.mock_sts,
        moto.mock_s3,
        moto.mock_iam,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bsm.s3_client.create_bucket(Bucket="bucket1")
        cls.bsm.s3_client.create_bucket(Bucket="bucket2")
        cls.bsm.iam_client.create_group(GroupName="Group1")
        cls.bsm.iam_client.create_group(GroupName="Group2")

    def test(self):
        res = list_resources(
            bsm=self.bsm,
            service="s3",
            method="list_buckets",
            is_paginator=False,
            boto_kwargs=None,
            result_path=ResultPath(path="Buckets"),
        )
        assert [dct["Name"] for dct in res.all()] == ["bucket1", "bucket2"]

        res = list_resources(
            bsm=self.bsm,
            service="iam",
            method="list_groups",
            is_paginator=True,
            boto_kwargs={
                "PaginationConfig": {
                    "MaxItems": 9999,
                    "PageSize": 1000,
                },
            },
            result_path=ResultPath(path="Groups"),
        )
        assert [dct["GroupName"] for dct in res.all()] == ["Group1", "Group2"]


def test_extract_tags():
    tag_data_1 = {"k1": "v1"}
    tag_data_2 = [{"Key": "k1", "Value": "v1"}]
    tag_data_3 = [{"key": "k1", "value": "v1"}]
    fields = [
        "tags",
        "Tags",
        "TagSet",
    ]
    for field in fields:
        for tag_data in [tag_data_1, tag_data_2, tag_data_3]:
            data = {field: tag_data}
            assert extract_tags(data) == {"k1": "v1"}

    with pytest.raises(ValueError):
        extract_tags({"tags": [{"KeyName": 1}]})

    with pytest.raises(TypeError):
        extract_tags({"tags": 1})


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.downloader",
        preview=False,
    )

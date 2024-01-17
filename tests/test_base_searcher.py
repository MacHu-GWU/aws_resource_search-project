# -*- coding: utf-8 -*-

import pytest
import moto

from aws_resource_search.tests.mock_test import BaseMockTest
from aws_resource_search.base_searcher import preprocess_query
from aws_resource_search.res.s3 import s3_bucket_searcher
from aws_resource_search.res.iam import iam_group_searcher


def test_preprocess_query():
    assert preprocess_query(None) == "*"
    assert preprocess_query("") == "*"
    assert preprocess_query("*") == "*"
    assert preprocess_query("abc") == "abc~1"
    assert preprocess_query("abc~2") == "abc~2"
    assert preprocess_query("abc xyz") == "abc~1 xyz~1"
    assert preprocess_query("abc~2 xyz") == "abc~2 xyz~1"
    assert preprocess_query("a") == "*"
    assert preprocess_query("a b c xyz") == "xyz~1"
    assert preprocess_query("s3.put_obj") == "s3~1 put~1 obj~1"
    assert preprocess_query("s*") == "s*~1"
    assert preprocess_query("s?") == "s?~1"


class TestSearcher(BaseMockTest):
    mock_list = [
        moto.mock_s3,
        moto.mock_iam,
        moto.mock_sts,
    ]

    def _create_test_buckets(self):
        self.bucket_names = [
            "company-data",
            "enterprise-data",
        ]
        for bucket_name in self.bucket_names:
            self.bsm.s3_client.create_bucket(Bucket=bucket_name)

    def _create_test_iam_groups(self):
        self.iam_group_names = [
            "admin_group",
            "developer_group",
        ]
        for iam_group_name in self.iam_group_names:
            try:
                self.bsm.iam_client.create_group(GroupName=iam_group_name)
            except Exception as e:
                if "already exists" in str(e):
                    pass
                else:
                    raise e

    def _test_get_bsm(self):
        with pytest.raises(TypeError):
            s3_bucket_searcher._get_bsm(bsm="bsm")
        s3_bucket_searcher._get_bsm(self.bsm)
        s3_bucket_searcher.bsm = self.bsm
        s3_bucket_searcher._get_bsm(self.bsm)

    def _test_search(self):
        self._create_test_buckets()
        s3_bucket_searcher.bsm = self.bsm
        res = s3_bucket_searcher.search(refresh_data=True)
        assert len(res) == 2

        res = s3_bucket_searcher.search(simple_response=False)
        assert len(res["hits"]) == 2

        self._create_test_iam_groups()
        iam_group_searcher.bsm = self.bsm
        res = iam_group_searcher.search(refresh_data=True)
        assert len(res) == 2

    def test(self):
        self._test_get_bsm()
        self._test_search()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.base_searcher", preview=False)

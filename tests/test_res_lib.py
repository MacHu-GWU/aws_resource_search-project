# -*- coding: utf-8 -*-

import moto
import pytest

import json
from datetime import datetime

import botocore.exceptions
from aws_resource_search.res_lib import (
    ResultPath,
    list_resources,
    extract_datetime,
    preprocess_query,
    BaseDocument,
)
from aws_resource_search.res.s3 import s3_bucket_searcher
from aws_resource_search.res.iam import iam_group_searcher
from aws_resource_search.tests.mock_test import BaseMockTest
from rich import print as rprint


class TestDocument:
    def _test_enrich_details(self):
        detail_items = []
        with BaseDocument.enrich_details(detail_items):
            detail_items.append("hello")
            raise botocore.exceptions.ClientError(
                error_response={}, operation_name="test"
            )
            detail_items.append("word")
        assert len(detail_items) == 2
        assert detail_items[0] == "hello"
        assert "❗" in detail_items[1].title

    def _test_one_line(self):
        assert BaseDocument.one_line("hello") == "hello"
        assert BaseDocument.one_line("hello\nword") == "hello ..."
        assert (
            BaseDocument.one_line(json.dumps(dict(a=1, b=2), indent=4))
            == '{"a": 1, "b": 2}'
        )
        assert BaseDocument.one_line("") == "NA"
        assert BaseDocument.one_line(None, "Not available") == "Not available"
        assert BaseDocument.one_line(dict(a=1, b=2)) == '{"a": 1, "b": 2}'

    def test(self):
        self._test_enrich_details()
        self._test_one_line()


class Test(BaseMockTest):
    mock_list = [
        moto.mock_s3,
        moto.mock_iam,
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

    def _test_list_resources_1_s3_not_paginator(self):
        def func():
            return list_resources(
                bsm=self.bsm,
                service="s3",
                method="list_buckets",
                is_paginator=False,
                boto_kwargs=None,
                result_path=ResultPath(path="Buckets"),
            ).all()

        assert len(func()) == 0
        self._create_test_buckets()
        res = func()
        assert len(res) == 2
        assert res[0]["Name"] == "company-data"
        assert res[1]["Name"] == "enterprise-data"

    def _test_list_resources_2_iam_is_paginator(self):
        def func():
            return list_resources(
                bsm=self.bsm,
                service="iam",
                method="list_groups",
                is_paginator=True,
                boto_kwargs=dict(
                    PaginationConfig=dict(
                        MaxItems=9999,
                        PageSize=1000,
                    )
                ),
                result_path=ResultPath(path="Groups"),
            ).all()

        assert len(func()) == 0
        self._create_test_iam_groups()
        res = func()
        assert len(res) == 2
        assert res[0]["GroupName"] == "admin_group"
        assert res[1]["GroupName"] == "developer_group"

    def _test_list_resources(self):
        self._test_list_resources_1_s3_not_paginator()
        self._test_list_resources_2_iam_is_paginator()

    def _test_preprocess_query(self):
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

    def _test_extract_datetime(self):
        assert extract_datetime({}, "create_time") == "No datetime"
        assert (
            extract_datetime({"create_time": datetime(2021, 1, 1)}, "create_time")
            == "2021-01-01T00:00:00"
        )
        assert extract_datetime({"create_time": "2021"}, "create_time") == "2021"

    def _test_extractor(self):
        self._test_extract_datetime()

    def _test_searcher_get_bsm(self):
        with pytest.raises(TypeError):
            s3_bucket_searcher._get_bsm()

        s3_bucket_searcher._get_bsm(self.bsm)
        s3_bucket_searcher.bsm = self.bsm
        s3_bucket_searcher._get_bsm(self.bsm)

    def _test_searcher_search(self):
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

    def _test_searcher(self):
        self._test_searcher_get_bsm()
        self._test_searcher_search()

    def test(self):
        self._test_list_resources()
        self._test_preprocess_query()
        self._test_extractor()
        self._test_searcher()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.res_lib", preview=False)

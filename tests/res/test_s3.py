# -*- coding: utf-8 -*-

import moto
from boto_session_manager import BotoSesManager
from aws_resource_search.res.s3 import S3Searcher
from aws_resource_search.tests.mock_test import BaseMockTest


class TestIamSearcher(BaseMockTest):
    mock_list = [
        moto.mock_s3,
        moto.mock_sts,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bsm = BotoSesManager()

        bucket_names = [
            "company-data",
            "enterprise-data",
        ]
        for bucket_name in bucket_names:
            cls.bsm.s3_client.create_bucket(Bucket=bucket_name)

    def test(self):
        sr = S3Searcher()

        assert len(sr.list_buckets()) == 2
        assert len(sr.list_buckets()) == 2

        assert "company" in sr.filter_buckets("company")[0].name
        assert "enterprise" in sr.filter_buckets("enterprise")[0].name


if __name__ == "__main__":
    from aws_resource_search.tests import run_cov_test

    run_cov_test(__file__, "aws_resource_search.res.s3", preview=False)
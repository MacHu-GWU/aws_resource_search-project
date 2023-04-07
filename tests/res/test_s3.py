# -*- coding: utf-8 -*-

import typing as T
import dataclasses
import os
import json

import moto
from boto_session_manager import BotoSesManager
from aws_resource_search.boto_ses import aws
from aws_resource_search.res.s3 import S3Searcher


class TestIamSearcher:
    mock_s3 = None

    @classmethod
    def setup_class(cls):
        cls.mock_s3 = moto.mock_s3()
        cls.mock_s3.start()

        aws.attach_bsm(BotoSesManager())

        bucket_names = [
            "company-data",
            "enterprise-data",
        ]
        for bucket_name in bucket_names:
            aws.bsm.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration=dict(
                    LocationConstraint=aws.bsm.aws_region,
                ),
            )

    @classmethod
    def teardown_class(cls):
        cls.mock_s3.stop()

    def test(self):
        sr = S3Searcher()
        assert len(sr.list_buckets()) == 2
        assert len(sr.list_buckets()) == 2

        assert "company" in sr.filter_buckets("company")[0].name
        assert "enterprise" in sr.filter_buckets("enterprise")[0].name


if __name__ == "__main__":
    from aws_resource_search.tests import run_cov_test

    run_cov_test(__file__, "aws_resource_search.res.s3", preview=False)

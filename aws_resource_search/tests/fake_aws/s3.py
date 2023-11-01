# -*- coding: utf-8 -*-

import typing as T

from .utils import guid, envs, rand_env

if T.TYPE_CHECKING:
    from .main import FakeAws


class S3Mixin:
    s3_buckets: T.List[str] = list()

    @classmethod
    def create_s3_bucket(cls: T.Type["FakeAws"]):
        for ith in range(1, 1 + 10):
            env = rand_env()
            bucket = f"{env}-{guid}-{ith}-s3-bucket"
            cls.bsm.s3_client.create_bucket(Bucket=bucket)
            cls.s3_buckets.append(bucket)

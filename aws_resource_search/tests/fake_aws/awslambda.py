# -*- coding: utf-8 -*-

import typing as T
import json
import random

from .utils import guid, envs, rand_env

if T.TYPE_CHECKING:
    from .main import FakeAws


class LambdaMixin:
    lambda_layers: T.List[str] = list()
    lambda_functions: T.List[str] = list()

    @classmethod
    def create_lambda_layers(
        cls: T.Type["FakeAws"],
        s3_bucket: T.Optional[str] = None,
    ):
        if s3_bucket is None:
            s3_bucket = random.choice(cls.s3_buckets)
        cls.bsm.s3_client.put_object(Bucket=s3_bucket, Key="my-layer.zip", Body=b"")
        for ith in range(1, 1 + 10):
            env = rand_env()
            name = f"{env}-{guid}-{ith}-lbd-layer"
            cls.bsm.lambda_client.publish_layer_version(
                LayerName=name,
                Content=dict(
                    S3Bucket=s3_bucket,
                    S3Key="my-key.zip",
                ),
            )
            cls.lambda_layers.append(name)

    @classmethod
    def create_lambda_functions(
        cls: T.Type["FakeAws"],
        s3_bucket: T.Optional[str] = None,
    ):
        cls.bsm.iam_client.create_role(
            RoleName=f"AwsLambdaDefaultRole",
            AssumeRolePolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
        )

        if s3_bucket is None:
            s3_bucket = random.choice(cls.s3_buckets)

        cls.bsm.s3_client.put_object(Bucket=s3_bucket, Key="my-source.zip", Body=b"")
        for ith in range(1, 1 + 10):
            env = rand_env()
            name = f"{env}-{guid}-{ith}-lbd-func"
            cls.bsm.lambda_client.create_function(
                FunctionName=name,
                Role="arn:aws:iam::123456789012:role/AwsLambdaDefaultRole",
                Handler="lambda_function.lambda_handler",
                MemorySize=256,
                Timeout=3,
                Code=dict(
                    S3Bucket=s3_bucket,
                    S3Key="my-key.zip",
                ),
            )
            cls.lambda_functions.append(name)

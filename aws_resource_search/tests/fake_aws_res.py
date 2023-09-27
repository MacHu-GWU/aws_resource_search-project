# -*- coding: utf-8 -*-

"""
Setup a fake AWS account with a lot of resources using moto
"""

import random
import uuid
import json
import moto
from faker import Faker
from .mock_test import BaseMockTest

fake = Faker()

guid = "e3f6"
envs = ["sbx", "tst", "prd"]


class FakeAws(BaseMockTest):
    mock_list = [
        moto.mock_ec2,
        moto.mock_s3,
        moto.mock_cloudformation,
    ]

    def create_ec2_inst(self):
        image_id = self.bsm.ec2_client.describe_images()["Images"][0]["ImageId"]

        for ith in range(1, 1 + 10):
            kwargs = dict(
                MinCount=1,
                MaxCount=1,
                ImageId=image_id,
            )
            if random.randint(1, 100) <= 70:
                env = random.choice(envs)
                kwargs["TagSpecifications"] = [
                    dict(
                        ResourceType="instance",
                        Tags=[dict(Key="Name", Value=f"{env}-{guid}-{ith}")],
                    )
                ]
            self.bsm.ec2_client.run_instances(**kwargs)

    def create_s3_bucket(self):
        for ith in range(1, 1 + 10):
            env = random.choice(envs)
            self.bsm.s3_client.create_bucket(Bucket=f"{env}-{guid}-{ith}")

    def create_cloudformation_stack(self):
        tpl_data = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Parameters": {
                "BucketName": {
                    "Type": "String",
                }
            },
            "Resources": {
                "S3Bucket": {
                    "Type": "AWS::S3::Bucket",
                    "Properties": {
                        "BucketName": {"Ref": "BucketName"},
                    },
                },
            },
        }
        for ith in range(1, 1 + 10):
            env = random.choice(envs)
            self.bsm.cloudformation_client.create_stack(
                StackName=f"{env}-{guid}-{ith}",
                TemplateBody=str(json.dumps(tpl_data)),
                Parameters=[
                    dict(
                        ParameterKey="BucketName",
                        ParameterValue=f"cft-managed-{ith}",
                    )
                ],
            )

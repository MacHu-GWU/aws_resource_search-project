# -*- coding: utf-8 -*-

"""
Setup a fake AWS account with a lot of resources using moto
"""

import random
import json
import moto
from faker import Faker
from .mock_test import BaseMockTest

fake = Faker()

guid = "e3f6"
envs = ["sbx", "tst", "prd"]


class FakeAws(BaseMockTest):
    mock_list = [
        moto.mock_cloudformation,
        moto.mock_dynamodb,
        moto.mock_ec2,
        moto.mock_glue,
        moto.mock_iam,
        moto.mock_s3,
    ]

    @classmethod
    def create_cloudformation_stack(cls):
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
            cls.bsm.cloudformation_client.create_stack(
                StackName=f"{env}-{guid}-{ith}-cloudformation-stack",
                TemplateBody=str(json.dumps(tpl_data)),
                Parameters=[
                    dict(
                        ParameterKey="BucketName",
                        ParameterValue=f"cft-managed-{ith}",
                    )
                ],
            )

    @classmethod
    def create_dynamodb_table(cls):
        for ith in range(1, 1 + 10):
            env = random.choice(envs)
            table = f"{env}-{guid}-{ith}-dynamodb-table"
            kwargs = dict(
                TableName=table,
                AttributeDefinitions=[
                    dict(
                        AttributeName="pk",
                        AttributeType="S",
                    ),
                ],
                KeySchema=[
                    dict(
                        AttributeName="pk",
                        KeyType="HASH",
                    )
                ],
                BillingMode="PAY_PER_REQUEST",
            )
            if random.randint(1, 100) <= 30:
                kwargs["AttributeDefinitions"].append(
                    dict(
                        AttributeName="sk",
                        AttributeType="S",
                    )
                )
                kwargs["KeySchema"].append(
                    dict(
                        AttributeName="sk",
                        KeyType="RANGE",
                    )
                )
            cls.bsm.dynamodb_client.create_table(**kwargs)

    @classmethod
    def create_ec2_inst(cls):
        image_id = cls.bsm.ec2_client.describe_images()["Images"][0]["ImageId"]

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
                        Tags=[
                            dict(Key="Name", Value=f"{env}-{guid}-{ith}-ec2-instance")
                        ],
                    )
                ]
            cls.bsm.ec2_client.run_instances(**kwargs)

    @classmethod
    def create_iam(cls):
        for ith in range(1, 1 + 10):
            env = random.choice(envs)
            cls.bsm.iam_client.create_role(
                RoleName=f"{env}-{guid}-{ith}-iam-role",
                AssumeRolePolicyDocument="{}",
            )

            cls.bsm.iam_client.create_policy(
                PolicyName=f"{env}-{guid}-{ith}-iam-policy",
                PolicyDocument=json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {"Effect": "Allow", "Action": "*", "Resource": "*"}
                        ],
                    }
                ),
            )

            cls.bsm.iam_client.create_user(
                UserName=f"{env}-{guid}-{ith}-iam-user",
            )

            cls.bsm.iam_client.create_group(
                GroupName=f"{env}-{guid}-{ith}-iam-group",
            )

    @classmethod
    def create_glue_database_table_job_and_crawler(cls):
        for ith in range(6):
            env = random.choice(envs)
            db_name = f"{env}-{guid}-{ith}-glue-database"
            cls.bsm.glue_client.create_database(
                DatabaseInput=dict(
                    Name=db_name,
                ),
            )
            for jth in range(10):
                tb_name = f"{env}-{guid}-{jth}-glue-table"
                cls.bsm.glue_client.create_table(
                    DatabaseName=db_name,
                    TableInput=dict(
                        Name=tb_name,
                    ),
                )

        for ith in range(10):
            env = random.choice(envs)
            job_name = f"{env}-{guid}-{ith}-glue-job"
            cls.bsm.glue_client.create_job(
                Name=job_name,
                Role="arn:aws:iam::123456789012:role/AWSGlueServiceRoleDefault",
                Command={
                    "Name": "glueetl",
                },
            )

        for ith in range(10):
            env = random.choice(envs)
            job_name = f"{env}-{guid}-{ith}-glue-crawler"
            cls.bsm.glue_client.create_crawler(
                Name=job_name,
                Role="arn:aws:iam::123456789012:role/AWSGlueServiceRoleDefault",
                Targets=dict(S3Targets=[]),
            )

    @classmethod
    def create_s3_bucket(cls):
        for ith in range(1, 1 + 10):
            env = random.choice(envs)
            cls.bsm.s3_client.create_bucket(Bucket=f"{env}-{guid}-{ith}-s3-bucket")

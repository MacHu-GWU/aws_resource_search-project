# -*- coding: utf-8 -*-

"""
Setup a fake AWS account with a lot of resources using moto for testing.
"""

import typing as T
import random
import json
import moto
from faker import Faker
from .mock_test import BaseMockTest

fake = Faker()

guid = "e3f6"
envs = ["sbx", "tst", "prd"]


class FakeAws(BaseMockTest):
    """
    .. note::

        methods are sorted alphabetically.
    """

    mock_list = [
        moto.mock_cloudformation,
        moto.mock_dynamodb,
        moto.mock_ec2,
        moto.mock_glue,
        moto.mock_iam,
        moto.mock_s3,
        moto.mock_lambda,
    ]

    # @classmethod
    # def create_cloudformation_stack(cls):
    #     tpl_data = {
    #         "AWSTemplateFormatVersion": "2010-09-09",
    #         "Parameters": {
    #             "BucketName": {
    #                 "Type": "String",
    #             }
    #         },
    #         "Resources": {
    #             "S3Bucket": {
    #                 "Type": "AWS::S3::Bucket",
    #                 "Properties": {
    #                     "BucketName": {"Ref": "BucketName"},
    #                 },
    #             },
    #         },
    #     }
    #     for ith in range(1, 1 + 10):
    #         env = random.choice(envs)
    #         cls.bsm.cloudformation_client.create_stack(
    #             StackName=f"{env}-{guid}-{ith}-cloudformation-stack",
    #             TemplateBody=str(json.dumps(tpl_data)),
    #             Parameters=[
    #                 dict(
    #                     ParameterKey="BucketName",
    #                     ParameterValue=f"cft-managed-{ith}",
    #                 )
    #             ],
    #         )
    #
    # @classmethod
    # def create_dynamodb_table(cls):
    #     for ith in range(1, 1 + 10):
    #         env = random.choice(envs)
    #         table = f"{env}-{guid}-{ith}-dynamodb-table"
    #         kwargs = dict(
    #             TableName=table,
    #             AttributeDefinitions=[
    #                 dict(
    #                     AttributeName="pk",
    #                     AttributeType="S",
    #                 ),
    #             ],
    #             KeySchema=[
    #                 dict(
    #                     AttributeName="pk",
    #                     KeyType="HASH",
    #                 )
    #             ],
    #             BillingMode="PAY_PER_REQUEST",
    #         )
    #         if random.randint(1, 100) <= 30:
    #             kwargs["AttributeDefinitions"].append(
    #                 dict(
    #                     AttributeName="sk",
    #                     AttributeType="S",
    #                 )
    #             )
    #             kwargs["KeySchema"].append(
    #                 dict(
    #                     AttributeName="sk",
    #                     KeyType="RANGE",
    #                 )
    #             )
    #         cls.bsm.dynamodb_client.create_table(**kwargs)

    # @classmethod
    # def create_ec2_inst(cls):
    #     image_id = cls.bsm.ec2_client.describe_images()["Images"][0]["ImageId"]
    #
    #     for ith in range(1, 1 + 10):
    #         kwargs = dict(
    #             MinCount=1,
    #             MaxCount=1,
    #             ImageId=image_id,
    #         )
    #         if random.randint(1, 100) <= 70:
    #             env = random.choice(envs)
    #             kwargs["TagSpecifications"] = [
    #                 dict(
    #                     ResourceType="instance",
    #                     Tags=[
    #                         dict(Key="Name", Value=f"{env}-{guid}-{ith}-ec2-instance")
    #                     ],
    #                 )
    #             ]
    #         cls.bsm.ec2_client.run_instances(**kwargs)

    # @classmethod
    # def create_ec2_vpc(cls) -> T.List[str]:
    #     vpc_id_list = list()
    #     for ith, env in enumerate(envs, start=1):
    #         kwargs = {
    #             "CidrBlock": f"10.{ith}.0.0/16",
    #             "TagSpecifications": [
    #                 dict(
    #                     ResourceType="vpc",
    #                     Tags=[dict(Key="Name", Value=f"{env}-{guid}-vpc")],
    #                 )
    #             ],
    #         }
    #         res = cls.bsm.ec2_client.create_vpc(**kwargs)
    #         vpc_id = res["Vpc"]["VpcId"]
    #         vpc_id_list.append(vpc_id)
    #     return vpc_id_list
    #
    # @classmethod
    # def create_ec2_subnet(cls, vpc_id_list: T.List[str]):
    #     for ith_vpc, vpc_id in enumerate(vpc_id_list, start=1):
    #         for ith_subnet, env in enumerate(envs, start=1):
    #             kwargs = {
    #                 "CidrBlock": f"10.{ith_vpc}.{ith_subnet}.0/24",
    #                 "TagSpecifications": [
    #                     dict(
    #                         ResourceType="subnet",
    #                         Tags=[
    #                             dict(Key="Name", Value=f"{vpc_id}/{env}-{guid}-subnet")
    #                         ],
    #                     )
    #                 ],
    #             }
    #             if vpc_id:
    #                 kwargs["VpcId"] = vpc_id
    #             res = cls.bsm.ec2_client.create_subnet(**kwargs)
    #
    # @classmethod
    # def create_ec2_securitygroup(cls, vpc_id_list: T.List[str] = None):
    #     if vpc_id_list is None:
    #         vpc_id_list = []
    #     for vpc_id in (None, *vpc_id_list):
    #         for ith, env in enumerate(envs, start=1):
    #             kwargs = {
    #                 "GroupName": f"{env}-{guid}-security-group",
    #                 "Description": "fake security group",
    #                 "TagSpecifications": [
    #                     dict(
    #                         ResourceType="security-group",
    #                         Tags=[
    #                             dict(
    #                                 Key="Name",
    #                                 Value=f"{vpc_id}/{env}-{guid}-security-group",
    #                             )
    #                         ],
    #                     )
    #                 ],
    #             }
    #             if vpc_id:
    #                 kwargs["VpcId"] = vpc_id
    #             res = cls.bsm.ec2_client.create_security_group(**kwargs)

    # @classmethod
    # def create_iam(cls):
    #     for ith in range(1, 1 + 10):
    #         env = random.choice(envs)
    #         cls.bsm.iam_client.create_role(
    #             RoleName=f"{env}-{guid}-{ith}-iam-role",
    #             AssumeRolePolicyDocument="{}",
    #         )
    #
    #         cls.bsm.iam_client.create_policy(
    #             PolicyName=f"{env}-{guid}-{ith}-iam-policy",
    #             PolicyDocument=json.dumps(
    #                 {
    #                     "Version": "2012-10-17",
    #                     "Statement": [
    #                         {"Effect": "Allow", "Action": "*", "Resource": "*"}
    #                     ],
    #                 }
    #             ),
    #         )
    #
    #         cls.bsm.iam_client.create_user(
    #             UserName=f"{env}-{guid}-{ith}-iam-user",
    #         )
    #
    #         cls.bsm.iam_client.create_group(
    #             GroupName=f"{env}-{guid}-{ith}-iam-group",
    #         )

    # @classmethod
    # def create_glue_database_table_job_and_crawler(cls):
    #     for ith in range(6):
    #         env = random.choice(envs)
    #         db_name = f"{env}-{guid}-{ith}-glue-database"
    #         cls.bsm.glue_client.create_database(
    #             DatabaseInput=dict(
    #                 Name=db_name,
    #             ),
    #         )
    #         for jth in range(10):
    #             tb_name = f"{env}-{guid}-{jth}-glue-table"
    #             cls.bsm.glue_client.create_table(
    #                 DatabaseName=db_name,
    #                 TableInput=dict(
    #                     Name=tb_name,
    #                 ),
    #             )
    #
    #     for ith in range(10):
    #         env = random.choice(envs)
    #         job_name = f"{env}-{guid}-{ith}-glue-job"
    #         cls.bsm.glue_client.create_job(
    #             Name=job_name,
    #             Role="arn:aws:iam::123456789012:role/AWSGlueServiceRoleDefault",
    #             Command={
    #                 "Name": "glueetl",
    #             },
    #         )
    #
    #     for ith in range(10):
    #         env = random.choice(envs)
    #         job_name = f"{env}-{guid}-{ith}-glue-crawler"
    #         cls.bsm.glue_client.create_crawler(
    #             Name=job_name,
    #             Role="arn:aws:iam::123456789012:role/AWSGlueServiceRoleDefault",
    #             Targets=dict(S3Targets=[]),
    #         )

    # @classmethod
    # def create_lambda_layers(cls, s3_bucket):
    #     cls.bsm.s3_client.put_object(Bucket=s3_bucket, Key="my-layer.zip", Body=b"")
    #     for ith in range(1, 1 + 10):
    #         env = random.choice(envs)
    #         cls.bsm.lambda_client.publish_layer_version(
    #             LayerName=f"{env}-{guid}-{ith}-lbd-layer",
    #             Content=dict(
    #                 S3Bucket=s3_bucket,
    #                 S3Key="my-key.zip",
    #             ),
    #         )
    #
    # @classmethod
    # def create_lambda_function(cls, s3_bucket):
    #     cls.bsm.iam_client.create_role(
    #         RoleName=f"AwsLambdaDefaultRole",
    #         AssumeRolePolicyDocument=json.dumps(
    #             {
    #                 "Version": "2012-10-17",
    #                 "Statement": [
    #                     {
    #                         "Effect": "Allow",
    #                         "Principal": {"Service": "lambda.amazonaws.com"},
    #                         "Action": "sts:AssumeRole",
    #                     }
    #                 ],
    #             }
    #         ),
    #     )
    #
    #     cls.bsm.s3_client.put_object(Bucket=s3_bucket, Key="my-source.zip", Body=b"")
    #     for ith in range(1, 1 + 10):
    #         env = random.choice(envs)
    #         cls.bsm.lambda_client.create_function(
    #             FunctionName=f"{env}-{guid}-{ith}-lbd-func",
    #             Role="arn:aws:iam::123456789012:role/AwsLambdaDefaultRole",
    #             Handler="lambda_function.lambda_handler",
    #             MemorySize=256,
    #             Timeout=3,
    #             Code=dict(
    #                 S3Bucket=s3_bucket,
    #                 S3Key="my-key.zip",
    #             ),
    #         )

    # @classmethod
    # def create_s3_bucket(cls) -> T.List[str]:
    #     s3_bucket_list = list()
    #     for ith in range(1, 1 + 10):
    #         env = random.choice(envs)
    #         bucket = f"{env}-{guid}-{ith}-s3-bucket"
    #         cls.bsm.s3_client.create_bucket(Bucket=bucket)
    #         s3_bucket_list.append(bucket)
    #     return s3_bucket_list

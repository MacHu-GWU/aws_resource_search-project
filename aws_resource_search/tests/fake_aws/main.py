# -*- coding: utf-8 -*-

"""
Set up a fake AWS account with a lot of resources using moto for testing.
"""

import moto

from ...paths import dir_unit_test
from ...ars import ARS
from ..mock_test import BaseMockTest

from .awslambda import LambdaMixin
from .cloudformation import CloudFormationMixin
from .dynamodb import DynamodbMixin
from .glue import GlueMixin
from .ec2 import Ec2Mixin
from .vpc import VpcMixin
from .s3 import S3Mixin
from .stepfunction import StepFunctionMixin
from .iam import IamMixin


class FakeAws(
    BaseMockTest,
    LambdaMixin,
    CloudFormationMixin,
    DynamodbMixin,
    GlueMixin,
    Ec2Mixin,
    VpcMixin,
    S3Mixin,
    StepFunctionMixin,
    IamMixin,
):
    """
    .. note::

        methods are sorted alphabetically.
    """

    mock_list = [
        moto.mock_apigateway,
        moto.mock_apigatewayv2,
        moto.mock_athena,
        moto.mock_batch,
        moto.mock_cloudformation,
        moto.mock_cloudwatch,
        moto.mock_codebuild,
        moto.mock_codecommit,
        moto.mock_codepipeline,
        moto.mock_dynamodb,
        moto.mock_ec2,
        moto.mock_ecr,
        moto.mock_ecs,
        moto.mock_events,
        moto.mock_firehose,
        moto.mock_glue,
        moto.mock_iam,
        moto.mock_kinesis,
        moto.mock_kms,
        moto.mock_lambda,
        moto.mock_rds,
        moto.mock_s3,
        moto.mock_sagemaker,
        moto.mock_sagemakerruntime,
        moto.mock_secretsmanager,
        moto.mock_ssm,
        moto.mock_stepfunctions,
        moto.mock_sts,
    ]

    ars: ARS

    @classmethod
    def create_all(cls):
        cls.create_cloudformation_stack()
        cls.create_dynamodb_tables()
        cls.create_ec2_instances()
        cls.create_vpc()
        cls.create_subnet()
        cls.create_security_group()
        cls.create_s3_bucket()
        cls.create_iam()
        cls.create_glue_database_table()
        cls.create_glue_job()
        cls.create_glue_crawler()
        cls.create_lambda_layers()
        cls.create_lambda_functions()
        cls.create_state_machines()

    @classmethod
    def setup_ars(cls):
        cls.ars = ARS(
            bsm=cls.bsm,
            dir_index=dir_unit_test.joinpath(".index"),
            dir_cache=dir_unit_test.joinpath(".cache"),
        )

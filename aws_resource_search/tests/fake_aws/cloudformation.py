# -*- coding: utf-8 -*-

import typing as T
import json

from .utils import guid, envs, rand_env

if T.TYPE_CHECKING:
    from .main import FakeAws


class CloudFormationMixin:
    cloudformation_stacks: T.List[str] = list()

    @classmethod
    def create_cloudformation_stack(cls: T.Type["FakeAws"]):
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
            env = rand_env()
            stack_name = f"{env}-{guid}-{ith}-cloudformation-stack"
            cls.bsm.cloudformation_client.create_stack(
                StackName=stack_name,
                TemplateBody=str(json.dumps(tpl_data)),
                Parameters=[
                    dict(
                        ParameterKey="BucketName",
                        ParameterValue=f"cft-managed-{ith}",
                    )
                ],
            )
            cls.cloudformation_stacks.append(stack_name)
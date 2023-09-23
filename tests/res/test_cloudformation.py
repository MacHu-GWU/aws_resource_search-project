# -*- coding: utf-8 -*-

import json
import moto
from boto_session_manager import BotoSesManager
from aws_resource_search.res.cloudformation import (
    Stack,
    StackSet,
    CloudFormationSearcher,
)
from aws_resource_search.tests.mock_test import BaseMockTest
from rich import print as rprint


class TestCloudFormationSearcher(BaseMockTest):
    mock_list = [
        moto.mock_cloudformation,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bsm = BotoSesManager()

        stack_names = [
            "my-app-dev",
            "my-app-test",
            "my-app-prod",
        ]
        for stack_name in stack_names:
            template = {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "S3Bucket": {
                        "Type": "AWS::S3::Bucket",
                        "Properties": {
                            "BucketName": f"{stack_name}-bucket",
                        },
                        "DeletionPolicy": "Retain",
                    }
                },
            }
            cls.bsm.cloudformation_client.create_stack(
                StackName=stack_name,
                TemplateBody=json.dumps(template),
            )

            cls.bsm.cloudformation_client.create_stack_set(
                StackSetName=stack_name,
                TemplateBody=json.dumps(template),
            )

    def test(self):
        sr = CloudFormationSearcher()
        res = sr.list_stacks()
        assert len(res) == 3
        assert isinstance(res[0], Stack)
        assert res[0].arn.startswith("arn:")

        assert sr.filter_stacks("dev")[0].name == "my-app-dev"
        assert sr.filter_stacks("test")[0].name == "my-app-test"
        assert sr.filter_stacks("prod")[0].name == "my-app-prod"

        res = sr.list_stack_sets()
        assert len(res) == 3
        assert res[0].arn.startswith("arn:")
        assert isinstance(res[0], StackSet)
        assert sr.filter_stack_sets("dev")[0].name == "my-app-dev"
        assert sr.filter_stack_sets("test")[0].name == "my-app-test"
        assert sr.filter_stack_sets("prod")[0].name == "my-app-prod"


if __name__ == "__main__":
    from aws_resource_search.tests import run_cov_test

    run_cov_test(__file__, "aws_resource_search.res.cloudformation", preview=False)

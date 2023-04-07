# -*- coding: utf-8 -*-

import typing as T
import dataclasses
import os
import json

import moto
from boto_session_manager import BotoSesManager
from aws_resource_search.boto_ses import aws
from aws_resource_search.res.iam import IamSearcher


class TestIamSearcher:
    mock_iam = None

    @classmethod
    def setup_class(cls):
        cls.mock_iam = moto.mock_iam()
        cls.mock_iam.start()

        aws.attach_bsm(BotoSesManager())

        cases = [
            ("ec2-admin",),
            ("lambda-admin",),
        ]
        for (name,) in cases:
            aws.bsm.iam_client.create_role(
                RoleName=f"{name}-role",
                AssumeRolePolicyDocument="{}",
            )

            aws.bsm.iam_client.create_policy(
                PolicyName=f"{name}-policy",
                PolicyDocument=json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {"Effect": "Allow", "Action": "*", "Resource": "*"}
                        ],
                    }
                ),
            )

    @classmethod
    def teardown_class(cls):
        cls.mock_iam.stop()

    def test(self):
        sr = IamSearcher()
        print(sr.list_roles())
        print(sr.list_roles())

        print(sr.filter_roles("ec2"))
        print(sr.filter_roles("lambda"))

        print(sr.list_policies(scope_is_all=True))
        print(sr.list_policies(scope_is_all=True))

        print(sr.filter_policies("ec2", scope_is_all=True))
        print(sr.filter_policies("lambda", scope_is_all=True))


if __name__ == "__main__":
    from aws_resource_search.tests import run_cov_test

    run_cov_test(__file__, "aws_resource_search.res.iam", preview=False)

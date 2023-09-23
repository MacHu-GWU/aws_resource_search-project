# -*- coding: utf-8 -*-

import json

import moto
from boto_session_manager import BotoSesManager
from aws_resource_search.res.iam import IamSearcher
from aws_resource_search.tests.mock_test import BaseMockTest
from rich import print as rprint


class TestIamSearcher(BaseMockTest):
    mock_list = [
        moto.mock_iam,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bsm = BotoSesManager()

        cases = [
            ("ec2-admin",),
            ("lambda-admin",),
        ]
        for (name,) in cases:
            cls.bsm.iam_client.create_role(
                RoleName=f"{name}-role",
                AssumeRolePolicyDocument="{}",
            )

            cls.bsm.iam_client.create_policy(
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

            cls.bsm.iam_client.create_user(
                UserName=f"{name}-user",
            )

    def test(self):
        sr = IamSearcher()
        assert len(sr.list_roles()) == 2
        assert len(sr.list_roles()) == 2

        assert "ec2" in sr.filter_roles("ec2")[0].name
        assert "lambda" in sr.filter_roles("lambda")[0].name

        assert len(sr.list_policies(scope_is_local=True)) == 2
        assert len(sr.list_policies(scope_is_local=True)) == 2

        assert "ec2" in sr.filter_policies("ec2", scope_is_local=True)[0].name
        assert "lambda" in sr.filter_policies("lambda", scope_is_local=True)[0].name

        assert len(sr.list_users()) == 2
        assert len(sr.list_users()) == 2

        assert "ec2" in sr.filter_users("ec2")[0].name
        assert "lambda" in sr.filter_users("lambda")[0].name


if __name__ == "__main__":
    from aws_resource_search.tests import run_cov_test

    run_cov_test(__file__, "aws_resource_search.res.iam", preview=False)

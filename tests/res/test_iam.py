# -*- coding: utf-8 -*-

import typing as T
import dataclasses
import os
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
            ("ec2-admin-role", ),
            ("lambda-admin-role",),
        ]
        for role_name, in cases:
            aws.bsm.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument="{}",
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


if __name__ == "__main__":
    from aws_resource_search.tests import run_cov_test

    run_cov_test(__file__, "aws_resource_search.res.iam", preview=False)

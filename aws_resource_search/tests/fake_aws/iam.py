# -*- coding: utf-8 -*-

import typing as T
import json

from .utils import guid, envs, rand_env

if T.TYPE_CHECKING:
    from .main import FakeAws


class IamMixin:
    iam_groups: T.List[str] = list()
    iam_users: T.List[str] = list()
    iam_roles: T.List[str] = list()
    iam_policies: T.List[str] = list()

    @classmethod
    def create_iam(cls: T.Type["FakeAws"]):
        for ith in range(1, 1 + 10):
            env = rand_env()

            name = f"{env}-{guid}-{ith}-iam-group"
            cls.bsm.iam_client.create_group(GroupName=name)
            cls.iam_groups.append(name)

            name = f"{env}-{guid}-{ith}-iam-user"
            cls.bsm.iam_client.create_user(UserName=name)
            cls.iam_users.append(name)

            name = f"{env}-{guid}-{ith}-iam-role"
            cls.bsm.iam_client.create_role(
                RoleName=name,
                AssumeRolePolicyDocument="{}",
            )
            cls.iam_roles.append(name)

            name = f"{env}-{guid}-{ith}-iam-policy"
            cls.bsm.iam_client.create_policy(
                PolicyName=name,
                PolicyDocument=json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {"Effect": "Allow", "Action": "*", "Resource": "*"}
                        ],
                    }
                ),
            )
            cls.iam_policies.append(name)

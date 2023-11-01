# -*- coding: utf-8 -*-

import moto

mock_list = [
    moto.mock_sts,
    moto.mock_s3,
    moto.mock_stepfunctions,
]
for mock_aws in mock_list:
    mock_aws().start()

import json
import random

from aws_resource_search.ui.boto_ses import bsm
from aws_resource_search.ui.main import run_ui

guid = "a1b2c3"
envs = ["sbx", "tst", "prd"]
projects = [
    "infrastructure",
    "machinelearning",
    "businessreport",
]


def rand_env() -> str:
    return random.choice(envs)


def rand_proj() -> str:
    return random.choice(projects)


# print(bsm.aws_account_id)
# print(bsm.aws_region)

# s3 bucket
n = 30
for ith in range(1, 1 + n):
    env = rand_env()
    project = rand_proj()
    bucket = f"i-{ith}-{env}-{guid}-{project}-s3-bucket"
    bsm.s3_client.create_bucket(Bucket=bucket)
    bsm.s3_client.put_bucket_tagging(
        Bucket=bucket,
        Tagging={
            "TagSet": [
                {"Key": "Environment", "Value": env},
                {"Key": "Project", "Value": project},
            ]
        },
    )

# sfn state machine and execution
n = 30
for ith in range(1, 1 + n):
    env = rand_env()
    project = rand_proj()
    name = f"i-{ith}-{env}-{guid}-{project}-sfn-state-machine"
    res = bsm.sfn_client.create_state_machine(
        name=name,
        definition=json.dumps(
            {
                "Comment": "A description of my state machine",
                "StartAt": "Pass",
                "States": {"Pass": {"Type": "Pass", "End": True}},
            }
        ),
        roleArn="arn:aws:iam::123456789012:role/AWSStepFunctionsServiceRoleDefault",
        type=random.choice(["STANDARD", "EXPRESS"]),
        tags=[
            {"key": "Environment", "value": env},
            {"key": "Project", "value": project},
        ],
    )
    arn = res["stateMachineArn"]
    for _ in range(3, 5):
        bsm.sfn_client.start_execution(stateMachineArn=arn)


if __name__ == "__main__":
    run_ui()

# -*- coding: utf-8 -*-

import typing as T
import random

from .utils import guid, envs, rand_env

if T.TYPE_CHECKING:
    from .main import FakeAws


class StepFunctionMixin:
    sfn_state_machines: T.List[str] = list()

    @classmethod
    def create_state_machines(cls: T.Type["FakeAws"]):
        for ith in range(1, 1 + 10):
            env = rand_env()
            name = f"{env}-{guid}-{ith}-sfn-state-machine"
            sm_type = random.choice(["STANDARD", "EXPRESS"])
            cls.bsm.sfn_client.create_state_machine(
                name=name,
                definition="{}",
                roleArn=f"arn:aws:iam::{cls.bsm.aws_account_id}:role/AWSStepFunctionRoleDefault",
                type=sm_type,
            )
            cls.sfn_state_machines.append(name)

            if sm_type == "STANDARD":
                sm_arn = f"arn:aws:states:{cls.bsm.aws_region}:{cls.bsm.aws_account_id}:stateMachine:{name}"
                cls.bsm.sfn_client.start_execution(stateMachineArn=sm_arn, input="{}")

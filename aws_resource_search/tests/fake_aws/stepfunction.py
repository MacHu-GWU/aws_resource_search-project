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
            cls.bsm.sfn_client.create_state_machine(
                name=name,
                definition="{}",
                roleArn="arn:aws:iam::123456789012:role/AWSStepFunctionRoleDefault",
                type=random.choice(["STANDARD", "EXPRESS"]),
            )
            cls.sfn_state_machines.append(name)

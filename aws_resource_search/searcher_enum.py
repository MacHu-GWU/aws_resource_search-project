# -*- coding: utf-8 -*-

from .vendor.better_enum import BetterStrEnum


class SearcherEnum(BetterStrEnum):
    iam_group = "iam-group"
    iam_policy = "iam-policy"
    iam_role = "iam-role"
    iam_user = "iam-user"
    s3_bucket = "s3-bucket"
    sfn_state_machine = "sfn-state-machine"
    sfn_state_machine_execution = "sfn-state-machine-execution"

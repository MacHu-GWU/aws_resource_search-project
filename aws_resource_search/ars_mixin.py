# -*- coding: utf-8 -*-

"""
See :class:`ARSMixin`
"""

import typing as T

from .compat import cached_property

if T.TYPE_CHECKING:  # pragma: no cover
    from .ars_def import ARS
    from .res.iam import IamGroupSearcher
    from .res.iam import IamPolicySearcher
    from .res.iam import IamRoleSearcher
    from .res.iam import IamUserSearcher
    from .res.s3 import S3BucketSearcher
    from .res.sfn import SfnStateMachineSearcher
    from .res.sfn import SfnExecutionSearcher


class ARSMixin:  # pragma: no cover
    @cached_property
    def iam_group(self: "ARS") -> "IamGroupSearcher":
        return self.get_searcher("iam-group")

    @cached_property
    def iam_policy(self: "ARS") -> "IamPolicySearcher":
        return self.get_searcher("iam-policy")

    @cached_property
    def iam_role(self: "ARS") -> "IamRoleSearcher":
        return self.get_searcher("iam-role")

    @cached_property
    def iam_user(self: "ARS") -> "IamUserSearcher":
        return self.get_searcher("iam-user")

    @cached_property
    def s3_bucket(self: "ARS") -> "S3BucketSearcher":
        return self.get_searcher("s3-bucket")

    @cached_property
    def sfn_state_machine(self: "ARS") -> "SfnStateMachineSearcher":
        return self.get_searcher("sfn-state-machine")

    @cached_property
    def sfn_state_machine_execution(self: "ARS") -> "SfnExecutionSearcher":
        return self.get_searcher("sfn-state-machine-execution")

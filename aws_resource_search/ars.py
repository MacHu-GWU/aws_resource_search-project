# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from .ars_base import ARSBase
from .compat import cached_property
from .res_lib import Searcher

if T.TYPE_CHECKING:  # pragma: no cover
    from .res.iam import IamGroupSearcher
    from .res.iam import IamPolicySearcher
    from .res.iam import IamRoleSearcher
    from .res.iam import IamUserSearcher
    from .res.s3 import S3BucketSearcher


@dataclasses.dataclass
class ARS(ARSBase):  # pragma: no cover
    @cached_property
    def iam_group(self) -> "IamGroupSearcher":
        return self.get_searcher("iam-group")
    
    @cached_property
    def iam_policy(self) -> "IamPolicySearcher":
        return self.get_searcher("iam-policy")
    
    @cached_property
    def iam_role(self) -> "IamRoleSearcher":
        return self.get_searcher("iam-role")
    
    @cached_property
    def iam_user(self) -> "IamUserSearcher":
        return self.get_searcher("iam-user")
    
    @cached_property
    def s3_bucket(self) -> "S3BucketSearcher":
        return self.get_searcher("s3-bucket")
    
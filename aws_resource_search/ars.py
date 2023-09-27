# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from .ars_base import ARSBase
from .compat import cached_property

if T.TYPE_CHECKING:
    from .resource_searcher import ResourceSearcher


@dataclasses.dataclass
class ARS(ARSBase):
    @cached_property
    def cloudformation_stack(self) -> "ResourceSearcher":
        return self._get_rs(service_id="cloudformation", resource_type="stack")
    
    @cached_property
    def ec2_instance(self) -> "ResourceSearcher":
        return self._get_rs(service_id="ec2", resource_type="instance")
    
    @cached_property
    def iam_group(self) -> "ResourceSearcher":
        return self._get_rs(service_id="iam", resource_type="group")
    
    @cached_property
    def iam_user(self) -> "ResourceSearcher":
        return self._get_rs(service_id="iam", resource_type="user")
    
    @cached_property
    def iam_role(self) -> "ResourceSearcher":
        return self._get_rs(service_id="iam", resource_type="role")
    
    @cached_property
    def iam_policy(self) -> "ResourceSearcher":
        return self._get_rs(service_id="iam", resource_type="policy")
    
    @cached_property
    def s3_bucket(self) -> "ResourceSearcher":
        return self._get_rs(service_id="s3", resource_type="bucket")
    
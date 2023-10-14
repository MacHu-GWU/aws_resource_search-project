# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from .ars_base import ARSBase
from .compat import cached_property

if T.TYPE_CHECKING:  # pragma: no cover
    from .resource_searcher import ResourceSearcher


@dataclasses.dataclass
class ARS(ARSBase):  # pragma: no cover
    @cached_property
    def cloudformation_stack(self) -> "ResourceSearcher":
        return self._get_rs(service_id="cloudformation", resource_type="stack")
    
    @cached_property
    def codepipeline_pipeline(self) -> "ResourceSearcher":
        return self._get_rs(service_id="codepipeline", resource_type="pipeline")
    
    @cached_property
    def dynamodb_table(self) -> "ResourceSearcher":
        return self._get_rs(service_id="dynamodb", resource_type="table")
    
    @cached_property
    def ec2_instance(self) -> "ResourceSearcher":
        return self._get_rs(service_id="ec2", resource_type="instance")
    
    @cached_property
    def ec2_securitygroup(self) -> "ResourceSearcher":
        return self._get_rs(service_id="ec2", resource_type="securitygroup")
    
    @cached_property
    def ec2_subnet(self) -> "ResourceSearcher":
        return self._get_rs(service_id="ec2", resource_type="subnet")
    
    @cached_property
    def ec2_vpc(self) -> "ResourceSearcher":
        return self._get_rs(service_id="ec2", resource_type="vpc")
    
    @cached_property
    def glue_crawler(self) -> "ResourceSearcher":
        return self._get_rs(service_id="glue", resource_type="crawler")
    
    @cached_property
    def glue_database(self) -> "ResourceSearcher":
        return self._get_rs(service_id="glue", resource_type="database")
    
    @cached_property
    def glue_job(self) -> "ResourceSearcher":
        return self._get_rs(service_id="glue", resource_type="job")
    
    @cached_property
    def glue_table(self) -> "ResourceSearcher":
        return self._get_rs(service_id="glue", resource_type="table")
    
    @cached_property
    def iam_group(self) -> "ResourceSearcher":
        return self._get_rs(service_id="iam", resource_type="group")
    
    @cached_property
    def iam_policy(self) -> "ResourceSearcher":
        return self._get_rs(service_id="iam", resource_type="policy")
    
    @cached_property
    def iam_role(self) -> "ResourceSearcher":
        return self._get_rs(service_id="iam", resource_type="role")
    
    @cached_property
    def iam_user(self) -> "ResourceSearcher":
        return self._get_rs(service_id="iam", resource_type="user")
    
    @cached_property
    def lambda_function(self) -> "ResourceSearcher":
        return self._get_rs(service_id="lambda", resource_type="function")
    
    @cached_property
    def lambda_layer(self) -> "ResourceSearcher":
        return self._get_rs(service_id="lambda", resource_type="layer")
    
    @cached_property
    def s3_bucket(self) -> "ResourceSearcher":
        return self._get_rs(service_id="s3", resource_type="bucket")
    
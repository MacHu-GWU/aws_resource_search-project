# -*- coding: utf-8 -*-

import dataclasses

from .ars_base_v2 import ARSBase
from .compat import cached_property
from .res_lib import Searcher


@dataclasses.dataclass
class ARS(ARSBase):  # pragma: no cover
    @cached_property
    def cloudformation_stack(self) -> Searcher:
        return self._get_searcher("cloudformation-stack")
    
    @cached_property
    def codecommit_repository(self) -> Searcher:
        return self._get_searcher("codecommit-repository")
    
    @cached_property
    def ec2_instance(self) -> Searcher:
        return self._get_searcher("ec2-instance")
    
    @cached_property
    def ec2_securitygroup(self) -> Searcher:
        return self._get_searcher("ec2-securitygroup")
    
    @cached_property
    def ec2_subnet(self) -> Searcher:
        return self._get_searcher("ec2-subnet")
    
    @cached_property
    def ec2_vpc(self) -> Searcher:
        return self._get_searcher("ec2-vpc")
    
    @cached_property
    def glue_database(self) -> Searcher:
        return self._get_searcher("glue-database")
    
    @cached_property
    def glue_job(self) -> Searcher:
        return self._get_searcher("glue-job")
    
    @cached_property
    def glue_jobrun(self) -> Searcher:
        return self._get_searcher("glue-jobrun")
    
    @cached_property
    def glue_table(self) -> Searcher:
        return self._get_searcher("glue-table")
    
    @cached_property
    def iam_group(self) -> Searcher:
        return self._get_searcher("iam-group")
    
    @cached_property
    def iam_policy(self) -> Searcher:
        return self._get_searcher("iam-policy")
    
    @cached_property
    def iam_role(self) -> Searcher:
        return self._get_searcher("iam-role")
    
    @cached_property
    def iam_user(self) -> Searcher:
        return self._get_searcher("iam-user")
    
    @cached_property
    def lambda_function(self) -> Searcher:
        return self._get_searcher("lambda-function")
    
    @cached_property
    def lambda_layer(self) -> Searcher:
        return self._get_searcher("lambda-layer")
    
    @cached_property
    def s3_bucket(self) -> Searcher:
        return self._get_searcher("s3-bucket")
    
    @cached_property
    def sfn_execution(self) -> Searcher:
        return self._get_searcher("sfn-execution")
    
    @cached_property
    def sfn_statemachine(self) -> Searcher:
        return self._get_searcher("sfn-statemachine")
    
    @cached_property
    def sns_topic(self) -> Searcher:
        return self._get_searcher("sns-topic")
    
    @cached_property
    def sqs_queue(self) -> Searcher:
        return self._get_searcher("sqs-queue")
    
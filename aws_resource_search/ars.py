# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from .ars_base import ARSBase
from .compat import cached_property
from .res_lib import Searcher

if T.TYPE_CHECKING:  # pragma: no cover
    from .res.cloudformation import CloudFormationStackSearcher
    from .res.codebuild import CodeBuildJobRunSearcher
    from .res.codebuild import CodeBuildProjectSearcher
    from .res.codecommit import CodeCommitRepositorySearcher
    from .res.codepipeline import CodePipelinePipelineSearcher
    from .res.dynamodb import DynamodbTableSearcher
    from .res.ec2 import Ec2InstanceSearcher
    from .res.ec2 import Ec2SecurityGroupSearcher
    from .res.ec2 import Ec2SubnetSearcher
    from .res.ec2 import Ec2VpcSearcher
    from .res.ecr import EcrRepositorySearcher
    from .res.ecr import EcrRepositoryImageSearcher
    from .res.ecs import EcsClusterSearcher
    from .res.ecs import EcsTaskRunSearcher
    from .res.ecs import EcsTaskDefinitionFamilySearcher
    from .res.glue import GlueCrawlerSearcher
    from .res.glue import GlueDatabaseSearcher
    from .res.glue import GlueTableSearcher
    from .res.glue import GlueJobSearcher
    from .res.glue import GlueJobRunSearcher
    from .res.iam import IamGroupSearcher
    from .res.iam import IamPolicySearcher
    from .res.iam import IamRoleSearcher
    from .res.iam import IamUserSearcher
    from .res.kms import KmsKeyAliasSearcher
    from .res.awslambda import LambdaFunctionSearcher
    from .res.awslambda import LambdaFunctionAliasSearcher
    from .res.awslambda import LambdaLayerSearcher
    from .res.rds import Searcher
    from .res.rds import RdsDbInstanceSearcher
    from .res.s3 import S3BucketSearcher
    from .res.secretmanager import SecretsManagerSecretSearcher
    from .res.sfn import SfnStateMachineSearcher
    from .res.sfn import SfnExecutionSearcher
    from .res.sns import SnsTopicSearcher
    from .res.sqs import SqsQueueSearcher
    from .res.ssm import SsmParameterSearcher

@dataclasses.dataclass
class ARS(ARSBase):  # pragma: no cover
    @cached_property
    def cloudformation_stack(self) -> "CloudFormationStackSearcher":
        return self.get_searcher("cloudformation-stack")
    
    @cached_property
    def codebuild_job_run(self) -> "CodeBuildJobRunSearcher":
        return self.get_searcher("codebuild-job-run")
    
    @cached_property
    def codebuild_project(self) -> "CodeBuildProjectSearcher":
        return self.get_searcher("codebuild-project")
    
    @cached_property
    def codecommit_repository(self) -> "CodeCommitRepositorySearcher":
        return self.get_searcher("codecommit-repository")
    
    @cached_property
    def codepipeline_pipeline(self) -> "CodePipelinePipelineSearcher":
        return self.get_searcher("codepipeline-pipeline")
    
    @cached_property
    def dynamodb_table(self) -> "DynamodbTableSearcher":
        return self.get_searcher("dynamodb-table")
    
    @cached_property
    def ec2_instance(self) -> "Ec2InstanceSearcher":
        return self.get_searcher("ec2-instance")
    
    @cached_property
    def ec2_security_group(self) -> "Ec2SecurityGroupSearcher":
        return self.get_searcher("ec2-security-group")
    
    @cached_property
    def ec2_subnet(self) -> "Ec2SubnetSearcher":
        return self.get_searcher("ec2-subnet")
    
    @cached_property
    def ec2_vpc(self) -> "Ec2VpcSearcher":
        return self.get_searcher("ec2-vpc")
    
    @cached_property
    def ecr_repository(self) -> "EcrRepositorySearcher":
        return self.get_searcher("ecr-repository")
    
    @cached_property
    def ecr_repository_image(self) -> "EcrRepositoryImageSearcher":
        return self.get_searcher("ecr-repository-image")
    
    @cached_property
    def ecs_cluster(self) -> "EcsClusterSearcher":
        return self.get_searcher("ecs-cluster")
    
    @cached_property
    def ecs_task_run(self) -> "EcsTaskRunSearcher":
        return self.get_searcher("ecs-task-run")
    
    @cached_property
    def ecs_task_definition_family(self) -> "EcsTaskDefinitionFamilySearcher":
        return self.get_searcher("ecs_task_definition_family")
    
    @cached_property
    def glue_crawler(self) -> "GlueCrawlerSearcher":
        return self.get_searcher("glue-crawler")
    
    @cached_property
    def glue_database(self) -> "GlueDatabaseSearcher":
        return self.get_searcher("glue-database")
    
    @cached_property
    def glue_database_table(self) -> "GlueTableSearcher":
        return self.get_searcher("glue-database-table")
    
    @cached_property
    def glue_job(self) -> "GlueJobSearcher":
        return self.get_searcher("glue-job")
    
    @cached_property
    def glue_job_run(self) -> "GlueJobRunSearcher":
        return self.get_searcher("glue-job-run")
    
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
    def kms_key_alias(self) -> "KmsKeyAliasSearcher":
        return self.get_searcher("kms-key-alias")
    
    @cached_property
    def lambda_function(self) -> "LambdaFunctionSearcher":
        return self.get_searcher("lambda-function")
    
    @cached_property
    def lambda_function_alias(self) -> "LambdaFunctionAliasSearcher":
        return self.get_searcher("lambda-function-alias")
    
    @cached_property
    def lambda_layer(self) -> "LambdaLayerSearcher":
        return self.get_searcher("lambda-layer")
    
    @cached_property
    def rds_db_cluster(self) -> "Searcher":
        return self.get_searcher("rds-db-cluster")
    
    @cached_property
    def rds_db_instance(self) -> "RdsDbInstanceSearcher":
        return self.get_searcher("rds-db-instance")
    
    @cached_property
    def s3_bucket(self) -> "S3BucketSearcher":
        return self.get_searcher("s3-bucket")
    
    @cached_property
    def secretsmanager_secret(self) -> "SecretsManagerSecretSearcher":
        return self.get_searcher("secretsmanager-secret")
    
    @cached_property
    def sfn_state_machine(self) -> "SfnStateMachineSearcher":
        return self.get_searcher("sfn-state-machine")
    
    @cached_property
    def sfn_state_machine_execution(self) -> "SfnExecutionSearcher":
        return self.get_searcher("sfn-state-machine-execution")
    
    @cached_property
    def sns_topic(self) -> "SnsTopicSearcher":
        return self.get_searcher("sns-topic")
    
    @cached_property
    def sqs_queue(self) -> "SqsQueueSearcher":
        return self.get_searcher("sqs-queue")
    
    @cached_property
    def ssm_parameter(self) -> "SsmParameterSearcher":
        return self.get_searcher("ssm-parameter")
    
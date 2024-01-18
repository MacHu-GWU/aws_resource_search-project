# -*- coding: utf-8 -*-

"""
See :class:`ARSMixin`
"""

import typing as T

from .compat import cached_property

if T.TYPE_CHECKING:  # pragma: no cover
    from .ars_def import ARS
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
    from .res.rds import BaseSearcher
    from .res.rds import RdsDbInstanceSearcher
    from .res.s3 import S3BucketSearcher
    from .res.secretmanager import SecretsManagerSecretSearcher
    from .res.sfn import SfnStateMachineSearcher
    from .res.sfn import SfnExecutionSearcher
    from .res.sns import SnsTopicSearcher
    from .res.sqs import SqsQueueSearcher
    from .res.ssm import SsmParameterSearcher


class ARSMixin:  # pragma: no cover
    @cached_property
    def cloudformation_stack(self: "ARS") -> "CloudFormationStackSearcher":
        return self.get_searcher("cloudformation-stack")
    
    @cached_property
    def codebuild_job_run(self: "ARS") -> "CodeBuildJobRunSearcher":
        return self.get_searcher("codebuild-job-run")
    
    @cached_property
    def codebuild_project(self: "ARS") -> "CodeBuildProjectSearcher":
        return self.get_searcher("codebuild-project")
    
    @cached_property
    def codecommit_repository(self: "ARS") -> "CodeCommitRepositorySearcher":
        return self.get_searcher("codecommit-repository")
    
    @cached_property
    def codepipeline_pipeline(self: "ARS") -> "CodePipelinePipelineSearcher":
        return self.get_searcher("codepipeline-pipeline")
    
    @cached_property
    def dynamodb_table(self: "ARS") -> "DynamodbTableSearcher":
        return self.get_searcher("dynamodb-table")
    
    @cached_property
    def ec2_instance(self: "ARS") -> "Ec2InstanceSearcher":
        return self.get_searcher("ec2-instance")
    
    @cached_property
    def ec2_security_group(self: "ARS") -> "Ec2SecurityGroupSearcher":
        return self.get_searcher("ec2-security-group")
    
    @cached_property
    def ec2_subnet(self: "ARS") -> "Ec2SubnetSearcher":
        return self.get_searcher("ec2-subnet")
    
    @cached_property
    def ec2_vpc(self: "ARS") -> "Ec2VpcSearcher":
        return self.get_searcher("ec2-vpc")
    
    @cached_property
    def ecr_repository(self: "ARS") -> "EcrRepositorySearcher":
        return self.get_searcher("ecr-repository")
    
    @cached_property
    def ecr_repository_image(self: "ARS") -> "EcrRepositoryImageSearcher":
        return self.get_searcher("ecr-repository-image")
    
    @cached_property
    def ecs_cluster(self: "ARS") -> "EcsClusterSearcher":
        return self.get_searcher("ecs-cluster")
    
    @cached_property
    def ecs_task_run(self: "ARS") -> "EcsTaskRunSearcher":
        return self.get_searcher("ecs-task-run")
    
    @cached_property
    def ecs_task_definition_family(self: "ARS") -> "EcsTaskDefinitionFamilySearcher":
        return self.get_searcher("ecs_task_definition_family")
    
    @cached_property
    def glue_crawler(self: "ARS") -> "GlueCrawlerSearcher":
        return self.get_searcher("glue-crawler")
    
    @cached_property
    def glue_database(self: "ARS") -> "GlueDatabaseSearcher":
        return self.get_searcher("glue-database")
    
    @cached_property
    def glue_database_table(self: "ARS") -> "GlueTableSearcher":
        return self.get_searcher("glue-database-table")
    
    @cached_property
    def glue_job(self: "ARS") -> "GlueJobSearcher":
        return self.get_searcher("glue-job")
    
    @cached_property
    def glue_job_run(self: "ARS") -> "GlueJobRunSearcher":
        return self.get_searcher("glue-job-run")
    
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
    def kms_key_alias(self: "ARS") -> "KmsKeyAliasSearcher":
        return self.get_searcher("kms-key-alias")
    
    @cached_property
    def lambda_function(self: "ARS") -> "LambdaFunctionSearcher":
        return self.get_searcher("lambda-function")
    
    @cached_property
    def lambda_function_alias(self: "ARS") -> "LambdaFunctionAliasSearcher":
        return self.get_searcher("lambda-function-alias")
    
    @cached_property
    def lambda_layer(self: "ARS") -> "LambdaLayerSearcher":
        return self.get_searcher("lambda-layer")
    
    @cached_property
    def rds_db_cluster(self: "ARS") -> "BaseSearcher":
        return self.get_searcher("rds-db-cluster")
    
    @cached_property
    def rds_db_instance(self: "ARS") -> "RdsDbInstanceSearcher":
        return self.get_searcher("rds-db-instance")
    
    @cached_property
    def s3_bucket(self: "ARS") -> "S3BucketSearcher":
        return self.get_searcher("s3-bucket")
    
    @cached_property
    def secretsmanager_secret(self: "ARS") -> "SecretsManagerSecretSearcher":
        return self.get_searcher("secretsmanager-secret")
    
    @cached_property
    def sfn_state_machine(self: "ARS") -> "SfnStateMachineSearcher":
        return self.get_searcher("sfn-state-machine")
    
    @cached_property
    def sfn_state_machine_execution(self: "ARS") -> "SfnExecutionSearcher":
        return self.get_searcher("sfn-state-machine-execution")
    
    @cached_property
    def sns_topic(self: "ARS") -> "SnsTopicSearcher":
        return self.get_searcher("sns-topic")
    
    @cached_property
    def sqs_queue(self: "ARS") -> "SqsQueueSearcher":
        return self.get_searcher("sqs-queue")
    
    @cached_property
    def ssm_parameter(self: "ARS") -> "SsmParameterSearcher":
        return self.get_searcher("ssm-parameter")
    
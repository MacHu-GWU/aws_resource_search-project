# -*- coding: utf-8 -*-

"""
This module defines the search patterns for those resource types that requires
special handling.
"""

import typing as T

from .compat import TypedDict, cached_property
from .searcher_enum import SearcherEnum

if T.TYPE_CHECKING:
    from .ars_def import ARS


class T_SEARCH_PATTERN(TypedDict):
    partitioner_resource_type: str
    get_boto_kwargs: T.Callable


K_PARTITIONER_RESOURCE_TYPE = "partitioner_resource_type"
K_GET_BOTO_KWARGS = "get_boto_kwargs"


class ArsSearchPatternsMixin:
    """
    todo: docstring
    """
    def get_search_patterns(self: "ARS"):
        """
        This variable defines those resource types that requires a parent resource name
        for the boto3 API call. For example:

        - in order to search glue table, you need to specify glue database
        - in order to search glue job run, you need to specify glue job
        """
        return {
            SearcherEnum.ecr_repository_image.value: {
                K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.ecr_repository.value,
                K_GET_BOTO_KWARGS: lambda partitioner_query: {
                    "repositoryName": partitioner_query
                },
            },
            SearcherEnum.ecs_task_run.value: {
                K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.ecs_cluster.value,
                K_GET_BOTO_KWARGS: lambda partitioner_query: {
                    "cluster": partitioner_query
                },
            },
            SearcherEnum.glue_database_table.value: {
                K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.glue_database.value,
                K_GET_BOTO_KWARGS: lambda partitioner_query: {
                    "DatabaseName": partitioner_query
                },
            },
            SearcherEnum.glue_job_run.value: {
                K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.glue_job.value,
                K_GET_BOTO_KWARGS: lambda partitioner_query: {
                    "JobName": partitioner_query
                },
            },
            SearcherEnum.sfn_state_machine_execution: {
                K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.sfn_state_machine.value,
                K_GET_BOTO_KWARGS: lambda partitioner_query: {
                    "stateMachineArn": self.aws_console.step_function.get_state_machine_arn(
                        partitioner_query
                    )
                },
            },
            SearcherEnum.codebuild_job_run.value: {
                K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.codebuild_project.value,
                K_GET_BOTO_KWARGS: lambda partitioner_query: {
                    "projectName": partitioner_query
                },
            },
            SearcherEnum.lambda_function_alias.value: {
                K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.lambda_function.value,
                K_GET_BOTO_KWARGS: lambda partitioner_query: {
                    "FunctionName": partitioner_query
                },
            },
        }

    @cached_property
    def search_patterns(self: "ARS"):
        return self.get_search_patterns()

    def _clear_search_patterns_cache(self: "ARS"):
        """
        Clear the :meth:`ArsSearchPatternsMixin.search_patterns` cache.
        """
        del self.search_patterns

    def has_partitioner(
        self: "ARS",
        resource_type: str,
    ) -> bool:
        """
        Check if a resource type need a partitioner resource.
        """
        return resource_type in self.search_patterns

    def get_partitioner_resource_type(
        self: "ARS",
        resource_type: str,
    ) -> str:
        """
        Get the partitioner "resource type" of a resource type.
        """
        return self.search_patterns[resource_type][K_PARTITIONER_RESOURCE_TYPE]

    def get_partitioner_boto_kwargs(
        self: "ARS",
        resource_type: str,
        partitioner_query: str,
    ) -> dict:
        """
        Get the boto3 kwargs for the partitioner resource.
        """
        return self.search_patterns[resource_type][K_GET_BOTO_KWARGS](partitioner_query)

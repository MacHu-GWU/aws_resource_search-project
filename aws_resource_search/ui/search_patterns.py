# -*- coding: utf-8 -*-

"""
This module defines the search patterns for those resource types that requires
special handling.
"""

from ..searchers import SearcherEnum

from .boto_ses import ars


K_PARTITIONER_RESOURCE_TYPE = "partitioner_resource_type"
K_GET_BOTO_KWARGS = "get_boto_kwargs"

# This variable defines those resource types that requires a parent resource name
# for the boto3 API call. For example:
#
# - in order to search glue table, you need to specify glue database
# - in order to search glue job run, you need to specify glue job
has_partitioner_search_patterns = {
    SearcherEnum.glue_table: {
        K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.glue_database,
        K_GET_BOTO_KWARGS: lambda partitioner_query: {
            "DatabaseName": partitioner_query
        },
    },
    SearcherEnum.glue_jobrun: {
        K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.glue_job,
        K_GET_BOTO_KWARGS: lambda partitioner_query: {"JobName": partitioner_query},
    },
    SearcherEnum.sfn_execution: {
        K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.sfn_statemachine,
        K_GET_BOTO_KWARGS: lambda partitioner_query: {
            "stateMachineArn": ars.aws_console.step_function.get_state_machine_arn(
                partitioner_query
            )
        },
    },
}


def has_partitioner(resource_type: str) -> bool:
    return resource_type in has_partitioner_search_patterns


def get_partitioner_resource_type(resource_type: str) -> str:
    dct = has_partitioner_search_patterns[resource_type]
    return dct[K_PARTITIONER_RESOURCE_TYPE]


def get_partitioner_boto_kwargs(
    resource_type: str,
    partitioner_query: str,
) -> dict:
    dct = has_partitioner_search_patterns[resource_type]
    return dct[K_GET_BOTO_KWARGS](partitioner_query)

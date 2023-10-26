# -*- coding: utf-8 -*-

import zelfred.api as zf

from ..searchers import SearcherEnum

from .boto_ses import ars


def repaint_ui(ui: zf.UI):
    """
    Repaint the UI right after the items is ready. This is useful when you want
    to show a message before running the real handler.
    """
    # you should handle the ``ui.run_handler()`` logic yourself
    ui.move_to_end()
    ui.clear_items()
    ui.clear_query()
    ui.print_query()
    ui.print_items()


K_PARTITIONER_RESOURCE_TYPE = "partitioner_resource_type"
K_GET_BOTO_KWARGS = "get_boto_kwargs"

# This mapper is used to specify those resource types that require
# a parent resource name for the boto3 API call.
# for example,
# in order to search glue table, you need to specify glue database
# in order to search glue job run, you need to specify glue job
_has_partitioner_mapper = {
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

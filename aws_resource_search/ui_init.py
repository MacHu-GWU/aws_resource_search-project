# -*- coding: utf-8 -*-

import typing as T

import zelfred.api as zf

from . import res_lib_v1 as rl
from .handlers.api import (
    search_aws_profile_handler,
    search_resource_type_handler,
    search_resource_handler,
    show_aws_info_handler,
)
from .ars_init import ars
from .ui_def import UI


def handler(
    query: str,
    ui: "UI",
    skip_ui: bool = False,
) -> T.List[
    T.Union[
        rl.ShowAwsInfoItem,
        rl.SetAwsProfileItem,
        rl.AwsResourceTypeItem,
        rl.AwsResourceItem,
        rl.DetailItem,
        rl.ExceptionItem,
        rl.FileItem,
        rl.InfoItem,
        rl.UrlItem,
    ]
]:
    """
    Main query handler. It parses the query and route the query to
    the corresponding sub handler.

    - :func:`~aws_resource_search.ui.search_resource_type.select_resource_type_handler`
    - :func:`~aws_resource_search.ui.search_resource.search_resource_handler`

    The query can be in one of these formats:

    todo ...

    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    zf.debugger.log(f"handler Query: {query!r}")

    # srv id is the service_id-resource_type compound identifier
    # req query is the query string for the resource search
    q = zf.QueryParser(delimiter=":").parse(query)

    # --- handle special commands ---
    # example: s3-bucket: my bucket!?
    if len(query.split("!?", 1)) > 1:
        line_input, _ = query.split("!?", 1)
        return show_aws_info_handler(
            ui=ui,
            line_input=line_input,
            skip_ui=skip_ui,
        )

    # example: s3-bucket: my bucket!@switch to another profile
    if len(query.split("!@", 1)) > 1:
        line_input, aws_profile_query = query.split("!@", 1)
        return search_aws_profile_handler(
            ui=ui,
            line_input=line_input,
            profile_query=aws_profile_query,
            skip_ui=skip_ui,
        )

    # example: "  "
    if len(q.trimmed_parts) == 0:
        return search_resource_type_handler(
            ui=ui,
            query="*",
            skip_ui=skip_ui,
        )

    # example:
    # - "ec2 inst"
    # - "s3-bucket"
    # - "ec2 inst: "
    # - "s3-bucket: "
    elif len(q.trimmed_parts) == 1:
        service_query = q.trimmed_parts[0]

        # example:
        # - "ec2 inst: "
        # - "s3-bucket: "
        if len(q.parts) == 1:
            return search_resource_type_handler(
                ui=ui,
                query=service_query,
                skip_ui=skip_ui,
            )

        # example:
        # - "ec2 inst"
        # - "s3-bucket"
        else:
            resource_query = query.split(":")[1].strip()

            # example: "s3-bucket"
            if ui.ars.searcher_finder.is_valid_resource_type(service_query):
                return search_resource_handler(
                    ui=ui,
                    resource_type=service_query,
                    query=resource_query,
                    skip_ui=skip_ui,
                )

            # example: "ec2 inst"
            else:
                return search_resource_type_handler(
                    ui=ui,
                    query=service_query,
                    skip_ui=skip_ui,
                )

    # example: "ec2 inst: something", "s3-bucket: something"
    else:
        # example:
        # - s3-bucket: resource query", "s3-bucket" is a valid srv_id
        # use "resource query" to search
        service_query = q.trimmed_parts[0]
        resource_query = query.split(":")[1].strip()
        if ui.ars.searcher_finder.is_valid_resource_type(service_query):
            return search_resource_handler(
                ui=ui,
                resource_type=service_query,
                query=resource_query,
                skip_ui=skip_ui,
            )

        # example: # ec2 inst: something", "ec2 inst" is not a valid srv_id
        else:
            return search_resource_type_handler(
                ui=ui,
                query=service_query,
                skip_ui=skip_ui,
            )


ui = UI(
    ars=ars,
    handler=handler,
    hello_message="Welcome to AWS Resource Search!",
    capture_error=False,
    terminal=rl.terminal,
)


def run_ui():
    """
    Run the AWS resource search UI. This is the entry point of the CLI command.
    """
    zf.debugger.reset()
    zf.debugger.enable()
    ui.run()

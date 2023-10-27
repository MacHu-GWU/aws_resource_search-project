# -*- coding: utf-8 -*-

import typing as T

import zelfred.api as zf

try:
    import pyperclip
except ImportError:
    pass

from ..searchers import searchers_metadata
from .search_resource_type import (
    AwsResourceTypeItem,
    select_resource_type_handler,
)
from .search_resource import (
    AwsResourceItem,
    search_resource_handler,
)


def is_valid_resource_type(resource_type: str) -> bool:
    """
    Check if the given resource_type is a valid value that we support.

    :param resource_type: for example, ec2-instance, s3-bucket
    """
    return resource_type in searchers_metadata


def handler(
    query: str,
    ui: zf.UI,
) -> T.List[T.Union[AwsResourceTypeItem, AwsResourceItem]]:
    """
    Main query handler. It parses the query and route the query to
    the corresponding sub handler.
    """
    zf.debugger.log(f"handler Query: {query!r}")

    # srv id is the service_id-resource_type compound identifier
    # req query is the query string for the resource search
    q = zf.QueryParser(delimiter=":").parse(query)

    # example: "  "
    if len(q.trimmed_parts) == 0:
        return select_resource_type_handler(ui=ui, query="*")

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
            return select_resource_type_handler(ui=ui, query=service_query)

        # example:
        # - "ec2 inst"
        # - "s3-bucket"
        else:
            resource_query = query.split(":")[1].strip()

            # example: "s3-bucket"
            if is_valid_resource_type(service_query):
                return search_resource_handler(
                    resource_type=service_query,
                    query=resource_query,
                    ui=ui,
                )

            # example: "ec2 inst"
            else:
                return select_resource_type_handler(ui=ui, query=service_query)

    # example: "ec2 inst: something", "s3-bucket: something"
    else:
        # example:
        # - s3-bucket: resource query", "s3-bucket" is a valid srv_id
        # use "resource query" to search
        service_query = q.trimmed_parts[0]
        resource_query = query.split(":")[1].strip()
        if is_valid_resource_type(service_query):
            return search_resource_handler(
                resource_type=service_query,
                query=resource_query,
                ui=ui,
            )

        # example: # ec2 inst: something", "ec2 inst" is not a valid srv_id
        else:
            return select_resource_type_handler(ui=ui, query=service_query)


def run_ui():
    zf.debugger.reset()
    zf.debugger.enable()
    ui = zf.UI(
        handler=handler,
        capture_error=False,
        quit_on_action=False,
    )
    ui.run()

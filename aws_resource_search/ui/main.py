# -*- coding: utf-8 -*-

"""
todo: doc string here
"""

import typing as T

import zelfred.api as zf

try:
    import pyperclip
except ImportError:
    pass

from ..searchers import searchers_metadata
from ..terminal import terminal
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

    :param resource_type: for example, ec2-instance, s3-bucket.
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


class UI(zf.UI):
    """
    todo: doc string here
    """
    def process_ctrl_b(self: "UI"):
        """
        If you are searching an AWS resource, it will remove the query but keep
        the resource type, so you can enter a new query. For example, if you are
        searching S3 buckets, and you enter ``"s3-bucket: my-bucket"``,
        then Ctrl + B will remove ``"my-bucket"`` and keep ``"s3-bucket: "``.

        If you are searching a sub resource, it will remove the query of the
        sub resource, so you can enter a new query. For example, if you are searching
        Step Function execution, and you enter ``"sfn-execution: my-statemachine@a1b2c3"``,
        then Ctrl + B will remove ``"a1b2c3"`` and keep ``"sfn-execution: my-statemachine@"``.
        """
        line = self.line_editor.line
        parts = line.split(":", 1)
        n_parts = len(parts)
        # "sfn-state" -> "sfn-state"
        if n_parts in [0, 1]:
            return
        # "sfn-statemachine:   " -> "sfn-statemachine: "
        elif bool(parts[1].strip()) is False:
            return
        else:
            chunks = parts[1].split("@", 1)
            n_chunks = len(chunks)
            # "sfn-statemachine: my-statemachine" -> "sfn-statemachine: "
            if n_chunks in [0, 1]:
                self.line_editor.clear_line()
                self.line_editor.enter_text(f"{parts[0]}: ")
                return
            # "sfn-statemachine: my-statemachine@  " -> "sfn-statemachine: "
            elif bool(chunks[1].strip()) is False:
                self.line_editor.clear_line()
                self.line_editor.enter_text(f"{parts[0]}: ")
                return
            # "sfn-statemachine: my-statemachine@a1b2c3d4  " -> "sfn-statemachine: my-statemachine@"
            else:
                self.line_editor.clear_line()
                self.line_editor.enter_text(line.split("@", 1)[0] + "@")
                return

    def remove_text_format(self, text: str) -> str:
        formats = [
            terminal.cyan,
            terminal.yellow,
            terminal.magenta,
            terminal.blue,
            terminal.normal,
        ]
        for c in formats:
            text = text.replace(c, "")
        return text


def run_ui():
    zf.debugger.reset()
    zf.debugger.enable()
    ui = UI(
        handler=handler,
        capture_error=False,
    )
    ui.render.terminal = terminal
    ui.run()

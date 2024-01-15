# -*- coding: utf-8 -*-

"""
Main UI module. It collects classes, functions from all sub-modules
and provides the main entry point for the UI.
"""

import typing as T

import zelfred.api as zf

try:
    import pyperclip
except ImportError:
    pass

from ..searchers import finder
from ..terminal import terminal
from ..res_lib import DetailItem, InfoItem, OpenUrlItem, OpenFileItem
from .show_aws_info import (
    ShowAwsInfoItem,
    show_aws_info_handler,
)
from .search_aws_profile import (
    SetAwsProfileItem,
    search_aws_profile_handler,
)
from .search_resource_type import (
    AwsResourceTypeItem,
    select_resource_type_handler,
)
from .search_resource import (
    AwsResourceItem,
    search_resource_handler,
)


def handler(
    query: str,
    ui: zf.UI,
    skip_ui: bool = False,
) -> T.List[
    T.Union[
        ShowAwsInfoItem,
        SetAwsProfileItem,
        AwsResourceTypeItem,
        AwsResourceItem,
        DetailItem,
        InfoItem,
        OpenUrlItem,
        OpenFileItem,
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
            query=aws_profile_query,
            skip_ui=skip_ui,
        )

    # example: "  "
    if len(q.trimmed_parts) == 0:
        return select_resource_type_handler(
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
            return select_resource_type_handler(
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
            if finder.is_valid_resource_type(service_query):
                return search_resource_handler(
                    ui=ui,
                    resource_type=service_query,
                    query=resource_query,
                    skip_ui=skip_ui,
                )

            # example: "ec2 inst"
            else:
                return select_resource_type_handler(
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
        if finder.is_valid_resource_type(service_query):
            return search_resource_handler(
                ui=ui,
                resource_type=service_query,
                query=resource_query,
                skip_ui=skip_ui,
            )

        # example: # ec2 inst: something", "ec2 inst" is not a valid srv_id
        else:
            return select_resource_type_handler(
                ui=ui,
                query=service_query,
                skip_ui=skip_ui,
            )


class UI(zf.UI):
    """
    todo: doc string here
    """

    def process_ctrl_b(self: "UI"):
        """
        If you are searching an AWS resource, it will remove the query but keep
        the resource type, so you can enter a new query. For example
        (``|`` is the cursor):

        Now::

            (Query) s3-bucket: my-bucket|

        After Ctrl + B::

            (Query) s3-bucket: |

        If you are searching a sub resource, it will remove the query of the
        sub resource, so you can enter a new query. For example:

        Now::

            (Query) sfn-execution: my-statemachine@a1b2c3|

        After Ctrl + B::

            (Query) sfn-execution: my-statemachine@|
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
        """
        Remove the terminal format from the given text.
        """
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
    """
    Run the AWS resource search UI. This is the entry point of the CLI command.
    """
    zf.debugger.reset()
    zf.debugger.enable()
    ui = UI(
        handler=handler,
        capture_error=False,
        terminal=terminal,
    )
    ui.run()

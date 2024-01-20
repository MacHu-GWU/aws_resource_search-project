# -*- coding: utf-8 -*-

"""
AWS Resource UI class declaration modules.
"""

import typing as T

import zelfred.api as zf

from . import res_lib as rl
from .handlers.api import (
    open_config_handler,
    search_aws_profile_handler,
    search_resource_type_handler,
    search_resource_handler,
    show_aws_info_handler,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from .ars_def import ARS


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
]:  # pragma: no cover
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

    # example: s3-bucket: my bucket!{
    if len(query.split("!{", 1)) > 1:
        line_input, sub_query = query.split("!{", 1)
        return open_config_handler(
            ui=ui,
            line_input=line_input,
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


class UI(zf.UI):
    """
    Extend the ``zelfred.UI`` class to add custom key bindings.
    """

    def __init__(
        self,
        ars: "ARS",
        **kwargs,
    ):
        self.ars: "ARS" = ars
        super().__init__(handler=handler, **kwargs)

    @classmethod
    def new(
        cls,
        ars: "ARS",
    ):
        """
        A factory method to create a new UI instance.
        """
        return UI(
            ars=ars,
            hello_message="Welcome to AWS Resource Search!",
            capture_error=False,
            terminal=rl.terminal,
        )

    def process_ctrl_b(self):  # pragma: no cover
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

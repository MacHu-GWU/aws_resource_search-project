# -*- coding: utf-8 -*-

"""
AWS Resource UI class declaration modules.
"""

import typing as T

import zelfred.api as zf

if T.TYPE_CHECKING:  # pragma: no cover
    from .ars import ARS


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
        super().__init__(**kwargs)

    def process_ctrl_b(self):
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

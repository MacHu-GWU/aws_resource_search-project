# -*- coding: utf-8 -*-

"""
Common utilities.
"""

import zelfred.api as zf


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

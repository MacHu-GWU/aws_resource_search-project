# -*- coding: utf-8 -*-

import zelfred.api as zf

from .ars_init import ars
from .ui_def import UI


ui = UI.new(ars)


def run_ui():
    """
    Run the AWS resource search UI. This is the entry point of the CLI command.
    """
    zf.debugger.reset()
    zf.debugger.enable()
    ui.run()

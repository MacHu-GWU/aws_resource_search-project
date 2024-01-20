# -*- coding: utf-8 -*-

"""
See :func:`open_config_handler`.
"""

import typing as T

from .. import res_lib as rl
from ..paths import path_config_json

if T.TYPE_CHECKING:  # pragma: no cover
    from ..ui_def import UI


def open_config_handler(
    ui: "UI",
    line_input: str,
    skip_ui: bool = False,
) -> T.List[rl.FileItem]:  # pragma: no cover
    """
    Show current AWS account information of the current boto session.

    :param line_input: the original query input by user before the ``!{``.
    """
    ui.render.prompt = f"(Query)"
    items = [
        rl.FileItem.from_file(
            path=path_config_json,
            title="🛠 Open ${HOME}/.aws_resource_search/config.json",
            uid=f"open-config",
            autocomplete=line_input,
        )
    ]
    return items

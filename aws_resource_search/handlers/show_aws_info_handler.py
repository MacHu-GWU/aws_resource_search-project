# -*- coding: utf-8 -*-

"""
See :func:`show_aws_info_handler`.
"""

import typing as T

from .. import res_lib as rl
from ..terminal import ShortcutEnum

if T.TYPE_CHECKING:
    from ..ui_def import UI


def show_aws_info_handler(
    ui: "UI",
    line_input: str,
    skip_ui: bool = False,
) -> T.List[rl.ShowAwsInfoItem]:
    """
    Show current AWS account information of the current boto session.

    :param line_input: the original query input by user before the ``!?``.
    """
    ui.render.prompt = f"(Query)"
    items = [
        rl.ShowAwsInfoItem(
            title="📝 See AWS Account Info of current boto session below",
            subtitle=(
                f"Hit {ShortcutEnum.TAB} or {ShortcutEnum.ENTER} to go back, "
                f"Hit {ShortcutEnum.CTRL_W} to pick another AWS profile"
            ),
            uid=f"info-0",
            autocomplete=line_input,
        )
    ]
    bsm = ui.ars.bsm
    pairs = [
        ("aws_account_alias", bsm.aws_account_alias),
        ("aws_account_id", bsm.aws_account_id),
        ("aws_region", bsm.aws_region),
    ]
    items.extend(
        [
            rl.ShowAwsInfoItem.from_key_value(
                key=key,
                value=value,
                autocomplete=line_input,
            )
            for ith, (key, value) in enumerate(pairs, start=1)
        ]
    )
    return items

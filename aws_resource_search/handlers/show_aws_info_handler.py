# -*- coding: utf-8 -*-

"""
See :func:`show_aws_info_handler`.
"""

import typing as T

from .. import res_lib as rl
from ..terminal import ShortcutEnum

if T.TYPE_CHECKING:  # pragma: no cover
    from ..ui_def import UI


def show_aws_info_handler(
    ui: "UI",
    line_input: str,
    skip_ui: bool = False,
) -> T.List[rl.ShowAwsInfoItem]:  # pragma: no cover
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
    for key in [
        "aws_account_alias",
        "aws_account_id",
        "aws_region",
    ]:
        try:
            value = getattr(bsm, key)
        except Exception as e:
            value = f"Unable to get, error: {e}"
        item = rl.ShowAwsInfoItem.from_key_value(
            key=key,
            value=value,
            autocomplete=line_input,
        )
        items.append(item)
    return items

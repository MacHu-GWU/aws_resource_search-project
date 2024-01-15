# -*- coding: utf-8 -*-

"""
This module defines the logic to switch between aws profile without leaving the app.
"""

import typing as T
import dataclasses

from ..compat import TypedDict
from ..res_lib import ArsBaseItem
from ..terminal import ShortcutEnum, format_key_value
from .boto_ses import bsm

if T.TYPE_CHECKING:
    from .main import UI


class ShowAwsInfoItemVariables(TypedDict):
    n_backspace: int


@dataclasses.dataclass
class ShowAwsInfoItem(ArsBaseItem):
    """
    Represent an item to display current AWS Account information

    :param variables: in AwsResourceItem, the variable is a dictionary including
        the original document object (not dict).
    """

    variables: ShowAwsInfoItemVariables = dataclasses.field(default_factory=dict)

    def enter_handler(self, ui: "UI"):
        pass

    def post_enter_handler(self, ui: "UI"):
        """
        Do "autocomplete".
        """
        ui.line_editor.clear_line()
        ui.line_editor.enter_text(self.autocomplete)

    def ctrl_w_handler(self, ui: "UI"):
        pass

    def post_ctrl_w_handler(self, ui: "UI"):
        """
        Do "autocomplete".
        """
        ui.line_editor.clear_line()
        ui.line_editor.enter_text(self.autocomplete + "!@")


def show_aws_info_handler(
    ui: "UI",
    line_input: str,
    skip_ui: bool = False,
) -> T.List[ShowAwsInfoItem]:
    """
    Show current AWS account information of the current boto session.
    """
    ui.render.prompt = f"(Query)"
    items = [
        ShowAwsInfoItem(
            title="📝 See AWS Account Info of current boto session below",
            subtitle=(
                f"Hit {ShortcutEnum.TAB} or {ShortcutEnum.ENTER} to go back, "
                f"Hit {ShortcutEnum.CTRL_W} to pick another AWS profile"
            ),
            uid=f"info-0",
            autocomplete=line_input,
        )
    ]
    pairs = [
        ("aws_account_alias", bsm.aws_account_alias),
        ("aws_account_id", bsm.aws_account_id),
        ("aws_region", bsm.aws_region),
    ]
    items.extend(
        [
            ShowAwsInfoItem(
                title=f"Current {format_key_value(key, value)}",
                subtitle=(
                    f"Hit {ShortcutEnum.TAB} or {ShortcutEnum.ENTER} to go back, "
                    f"Hit {ShortcutEnum.CTRL_W} to pick another AWS profile"
                ),
                uid=f"info-{ith}",
                autocomplete=line_input,
            )
            for ith, (key, value) in enumerate(pairs, start=1)
        ]
    )
    return items

# -*- coding: utf-8 -*-

"""
See :class:`ShowAwsInfoItem`.
"""

import typing as T
import dataclasses

from ..terminal import format_key_value, ShortcutEnum
from .base_item import BaseArsItem

if T.TYPE_CHECKING:  # pragma: no cover
    from ..ui_def import UI


@dataclasses.dataclass
class ShowAwsInfoItem(BaseArsItem):
    """
    Represent an item to display current AWS Account information
    """

    def enter_handler(self, ui: "UI"):  # pragma: no cover
        pass

    def post_enter_handler(self, ui: "UI"):  # pragma: no cover
        """
        Do "autocomplete".
        """
        ui.line_editor.clear_line()
        ui.line_editor.enter_text(self.autocomplete)

    def ctrl_w_handler(self, ui: "UI"):  # pragma: no cover
        pass

    def post_ctrl_w_handler(self, ui: "UI"):  # pragma: no cover
        """
        Do "autocomplete".
        """
        ui.line_editor.clear_line()
        ui.line_editor.enter_text(self.autocomplete + "!@")

    @classmethod
    def from_key_value(
        cls,
        key: str,
        value: str,
        autocomplete: str,
    ):
        """
        Factory method for :class:`ShowAwsInfoItem`.

        :param key: the name of the aws account detail
        :param value: the value of the aws account detail
        :param autocomplete: the existing query input before "!?" to recover to.
        """
        return cls(
            title=f"Current {format_key_value(key, value)}",
            subtitle=(
                f"Hit {ShortcutEnum.TAB} or {ShortcutEnum.ENTER} to go back, "
                f"Hit {ShortcutEnum.CTRL_W} to pick another AWS profile"
            ),
            uid=f"aws-account-info-{key}",
            autocomplete=autocomplete,
        )

# -*- coding: utf-8 -*-

"""
See :class:`FileItem`.
"""

import typing as T
import dataclasses
from pathlib import Path

import zelfred.api as zf

from ..terminal import ShortcutEnum
from ..compat import TypedDict
from .base_item import BaseArsItem


class T_FILE_ITEM_VARIABLES(TypedDict):
    path: Path


@dataclasses.dataclass
class FileItem(BaseArsItem):
    """
    Represent a file item in the dropdown menu.
    """

    variables: T_FILE_ITEM_VARIABLES = dataclasses.field(default_factory=dict)

    def enter_handler(self, ui: "zf.UI"):  # pragma: no cover
        """
        Behavior:

        - If we have a path, open it in the default app.
        - If not, nothing happens (most likely NOT)
        """
        if self.variables.get("path") is not None:
            self.open_file_or_print(ui, self.variables["path"])
        else:
            pass

    def ctrl_a_handler(self, ui: "zf.UI"):  # pragma: no cover
        """
        Behavior:

        - Copy the path to clipboard
        """
        if self.variables.get("path") is not None:
            self.copy_or_print(ui, str(self.variables["path"]))
        else:
            pass

    def ctrl_u_handler(self, ui: "zf.UI"):  # pragma: no cover
        """
        Behavior:

        - Copy the path to clipboard
        """
        self.ctrl_a_handler(ui)

    @classmethod
    def from_file(
        cls,
        path: Path,
        title: T.Optional[str] = None,
        subtitle: T.Optional[str] = None,
        uid: T.Optional[str] = None,
        arg: T.Optional[str] = None,
        autocomplete: T.Optional[str] = None,
    ):
        """
        Create one :class:`FileItem` from an ``pathlib.Path`` object.
        """
        if title is None:
            title = f"📄 {path}"
        if subtitle is None:
            subtitle = f"📄 {ShortcutEnum.ENTER} to open file, 📋 {ShortcutEnum.CTRL_A} to copy path"
        kwargs = dict(
            title=title,
            subtitle=subtitle,
            arg=arg,
            autocomplete=autocomplete,
            variables={"path": path},
        )
        if uid:
            kwargs["uid"] = uid
        return cls(**kwargs)

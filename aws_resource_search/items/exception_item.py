# -*- coding: utf-8 -*-

"""
See :class:`ExceptionItem`.
"""

import typing as T
import traceback
import dataclasses

import zelfred.api as zf

from ..terminal import ShortcutEnum
from ..compat import TypedDict
from ..paths import path_exception_item_txt
from .base_item import BaseArsItem


class T_EXCEPTION_ITEM_VARIABLES(TypedDict):
    error: Exception
    traceback: str


@dataclasses.dataclass
class ExceptionItem(BaseArsItem):
    """
    Represent a Python exception detail in the dropdown menu.
    """

    variables: T_EXCEPTION_ITEM_VARIABLES = dataclasses.field(default_factory=dict)

    def enter_handler(self, ui: "zf.UI"):  # pragma: no cover
        """
        Behavior:

        - If we have an exception, we write the traceback data
            ``path_exception_item_txt`` and open it in the default app.
        - If not, nothing happens (most likely NOT)
        """
        if self.variables.get("error") is not None:
            path_exception_item_txt.write_text(self.variables["traceback"])
            self.open_file_or_print(ui, path_exception_item_txt)
        else:
            pass

    @classmethod
    def from_error(
        cls,
        error: Exception,
        title: T.Optional[str] = None,
        subtitle: T.Optional[str] = None,
        uid: T.Optional[str] = None,
        arg: T.Optional[str] = None,
        autocomplete: T.Optional[str] = None,
    ):
        """
        Create one :class:`ExceptionItem` from an ``Exception`` object.
        """
        if title is None:
            title = f"❗ {error!r}"
        if subtitle is None:
            subtitle = f"📄 {ShortcutEnum.ENTER} to view error details"
        kwargs = dict(
            title=title,
            subtitle=subtitle,
            arg=arg,
            autocomplete=autocomplete,
            variables={"error": error, "traceback": traceback.format_exc(limit=50)},
        )
        if uid:
            kwargs["uid"] = uid
        return cls(**kwargs)

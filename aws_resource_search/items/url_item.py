# -*- coding: utf-8 -*-

"""
See :class:`UrlItem`.
"""

import typing as T
import dataclasses

import zelfred.api as zf

from ..terminal import ShortcutEnum
from ..compat import TypedDict
from .base_item import BaseArsItem


class T_URL_ITEM_VARIABLES(TypedDict):
    url: str


@dataclasses.dataclass
class UrlItem(BaseArsItem):
    """
    Represent an url item in the dropdown menu.
    """

    variables: T_URL_ITEM_VARIABLES = dataclasses.field(default_factory=dict)

    def enter_handler(self, ui: "zf.UI"):  # pragma: no cover
        """
        Behavior:

        - If we have an url, open it in the default browser.
        - If not, nothing happens (most likely NOT)
        """
        if self.variables.get("url") is not None:
            self.open_url_or_print(ui, self.variables["url"])
        else:
            pass

    def ctrl_a_handler(self, ui: "zf.UI"):  # pragma: no cover
        """
        Behavior:

        - Copy the url to clipboard
        """
        self.ctrl_u_handler(ui)

    def ctrl_u_handler(self, ui: "zf.UI"):  # pragma: no cover
        """
        Behavior:

        - Copy the url to clipboard
        """
        if self.variables.get("url") is not None:
            self.copy_or_print(ui, str(self.variables["url"]))
        else:
            pass

    @classmethod
    def from_url(
        cls,
        url: str,
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
            title = f"🌐 {url}"
        if subtitle is None:
            subtitle = f"🌐 {ShortcutEnum.ENTER} to  {ShortcutEnum.CTRL_A} or {ShortcutEnum.CTRL_U} to copy url"
        kwargs = dict(
            title=title,
            subtitle=subtitle,
            arg=arg,
            autocomplete=autocomplete,
            variables={"url": url},
        )
        if uid:
            kwargs["uid"] = uid
        return cls(**kwargs)

# -*- coding: utf-8 -*-

"""
todo: docstring
"""

import typing as T
import dataclasses

import zelfred.api as zf

try:
    import pyperclip
except ImportError:  # pragma: no cover
    pass

from ..terminal import ShortcutEnum, format_key_value
from ..compat import TypedDict
from .base_item import ArsBaseItem


class T_DETAIL_ITEM_VARIABLES(TypedDict):
    """
    .. note::

        Copy is more common than url in detail item.
    """
    copy: T.Optional[str]
    url: T.Optional[str]


@dataclasses.dataclass
class DetailItem(ArsBaseItem):
    """
    Represent a detail information of an AWS resource in the dropdown menu.

    **Why this class**

    1. We need to write logic to create ``Item`` in the
        ``aws_resource_search.res.${aws_service}.py`` source code.
        This class provides utility methods to make the code clean and descriptive.
    2. An ``Item`` usually comes with user action. We need to store the
        user action argument in ``variables`` and then implement the
        ``xyz_handler`` function to handle the user action. In this project,
        we have a very clear mind of user action patterns. This class provides
        utility methods to enable pre-defined user action smartly based
        on the input, so we no longer need to implement ``variables`` logics
        and ``xyz_handler`` functions in most cases.
    """

    variables: T_DETAIL_ITEM_VARIABLES = dataclasses.field(default_factory=dict)

    @classmethod
    def new(
        cls,
        title: str,
        subtitle: T.Optional[str] = None,
        copy: T.Optional[str] = None,
        url: T.Optional[str] = None,
        uid: T.Optional[str] = None,
        arg: T.Optional[str] = None,
        autocomplete: T.Optional[str] = None,
    ):
        """
        The factory method to create a new ``ArsBaseItem`` instance.

        :param title: first line of the item. It has a checkbox in front of it to
            indicate whether it is selected.
        :param subtitle: second line of the item.
        :param copy: the text to copy to clipboard.
        :param url: the url to open in browser.
        :param uid: item unique id. The UI use this to distinguish different items.
        :param arg: argument that will be passed to the action.
        :param autocomplete: the text that will be filled in the input box when
            user hits ``TAB`` key.
        """
        kwargs = dict(
            title=title,
            arg=arg,
            autocomplete=autocomplete,
            variables={"url": url, "copy": copy},
        )
        if uid:
            kwargs["uid"] = uid

        # fmt: off
        if subtitle is None:
            if url is not None and copy is not None:
                kwargs["subtitle"] = f"🌐 {ShortcutEnum.ENTER} to open url, 📋 {ShortcutEnum.CTRL_A} to copy value, 🔗 {ShortcutEnum.CTRL_U} to copy url."
            elif url is not None:
                kwargs["subtitle"] = f"🌐 {ShortcutEnum.ENTER} to open url, 📋 {ShortcutEnum.CTRL_A} or 🔗 {ShortcutEnum.CTRL_U} to copy url."
            elif copy is not None:
                kwargs["subtitle"] = f"📋 {ShortcutEnum.CTRL_A} or 🔗 {ShortcutEnum.CTRL_U} to copy value"
            elif autocomplete:
                kwargs["subtitle"] = f"Hit{ShortcutEnum.TAB} to auto complete."
            else:
                kwargs["subtitle"] = "No subtitle"
        # fmt: on
        else:
            kwargs["subtitle"] = subtitle
        return cls(**kwargs)

    def enter_handler(self, ui: "zf.UI"):  # pragma: no cover
        """
        Behavior:

        - If we have a URL, it will be opened in the browser or print the url
            to the terminal if the terminal device can not do so.
        - If not, the Enter key will function similarly to the Tab key,
            it will autocomplete.
        """
        if self.variables.get("url"):
            self.open_url_or_print(ui, self.variables["url"])
        elif self.autocomplete:
            ui.line_editor.clear_line()
            ui.line_editor.enter_text(self.autocomplete)
        else:
            pass

    def ctrl_a_handler(self, ui: "zf.UI"):  # pragma: no cover
        """
        Behavior:

        - If we have a copy text, it will copy the text to clipboard or print the text
            to the terminal if the terminal device can not do so.
        - If we don't have copy text but have url, then treat url as copy text.
        """
        if self.variables.get("copy"):
            self.copy_or_print(ui, self.variables["copy"])
        elif self.variables.get("url"):
            self.copy_or_print(ui, self.variables["url"])
        else:
            pass

    def ctrl_u_handler(self, ui: "zf.UI"):  # pragma: no cover
        """
        Behavior:

        - If we have an url, it will copy the url to clipboard or print the url
            to the terminal if the terminal device can not do so.
        - If we don't have URL but have copy text, then treat copy text as url.
        """
        if self.variables.get("url"):
            self.copy_or_print(ui, self.variables["url"])
        elif self.variables.get("copy"):
            self.copy_or_print(ui, self.variables["copy"])
        else:
            pass

    @classmethod
    def from_detail(
        cls,
        key: str,
        value: T.Any,
        key_text: T.Optional[str] = None,
        value_text: T.Optional[str] = None,
        url: T.Optional[str] = None,
        uid: T.Optional[str] = None,
    ):
        """
        A utility method to create :class`DetailItem` from structured detail information.

        This method will be used in
        :class:`aws_resource_search.searcher.base_document.BaseDocument.get_details`
        method.

        A 'detail' is just a simple key value pair. For example, for S3 bucket.
        the 'bucket_name' is the key and the 'your-bucket-name' is the value.

        :param key: key of the detail, it's the original data
        :param value: value of the detail, it's the original data. This is also
            the text that will be copied to clipboard when user tap `Ctrl + A``.
        :param key_text: the ``${key} = ${value}`` text to display in the UI.
            if not provided, use ``key`` as the text.
        :param value_text: the ``${key} = ${value}`` text to display in the UI.
            if not provided, use ``value`` as the text.
        :param url: if specified, user can hit Enter key to open the url in browser,
            and Ctrl + U to copy it.
        :param uid: this is for uid
        """
        if key_text is None:
            key_text = key
        if value_text is None:
            value_text = value
        return cls.new(
            title=format_key_value(key_text, value_text),
            uid=uid,
            copy=str(value),
            url=url,
        )

    @classmethod
    def from_env_vars(
        cls,
        env_vars: T.Dict[str, str],
        url: T.Optional[str] = None,
    ) -> T.List["DetailItem"]:
        """
        A utility method to create many :class`DetailItem` from
        environment variable key value pairs.
        """
        if env_vars:
            return [
                cls.new(
                    title=f"🎯 env var: {format_key_value(k, v)}",
                    uid=f"env_var-{k}",
                    copy=v,
                    url=url,
                )
                for k, v in env_vars.items()
            ]
        else:
            if url is None:
                subtitle = "No environment variables found."
            else:
                subtitle = None # auto create it
            return [
                cls.new(
                    title=f"🏷 env var: 🔴 No environment variable found.",
                    subtitle=subtitle,
                    uid=f"no-environment-variable-found",
                    url=url,
                )
            ]

    @classmethod
    def from_tags(
        cls,
        tags: T.Dict[str, str],
        url: T.Optional[str] = None,
    ) -> T.List["DetailItem"]:
        """
        Create MANY :class:`DetailItem` from AWS resource tag key value pairs.
        """
        if tags:
            return [
                cls.new(
                    title=f"🏷 tag: {format_key_value(k, v)}",
                    uid=f"tag {k}",
                    copy=v,
                    url=url,
                )
                for k, v in tags.items()
            ]
        else:
            if url is None:
                subtitle = "No tag found."
            else:
                subtitle = None # auto create it
            return [
                cls.new(
                    title=f"🏷 tag: 🔴 No tag found.",
                    subtitle=subtitle,
                    uid=f"no-tag-found",
                    url=url,
                )
            ]

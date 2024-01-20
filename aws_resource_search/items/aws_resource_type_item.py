# -*- coding: utf-8 -*-

"""
See :class:`AwsResourceTypeItem`.
"""

import typing as T
import dataclasses

from ..terminal import ShortcutEnum, format_resource_type
from ..compat import TypedDict

from .base_item import BaseArsItem

if T.TYPE_CHECKING:  # pragma: no cover
    from ..documents.resource_type_document import ResourceTypeDocument
    from ..ars_def import ARS
    from ..ui_def import UI


class T_AWS_RESOURCE_TYPE_ITEM_VARIABLES(TypedDict):
    """
    Type hint for the "variables" field in :class:`AwsResourceTypeItem`.
    """

    doc: "ResourceTypeDocument"
    resource_type: str
    console_url: T.Optional[str]


@dataclasses.dataclass
class AwsResourceTypeItem(BaseArsItem):
    """
    Represent an item in the resource type search result.
    """

    variables: T_AWS_RESOURCE_TYPE_ITEM_VARIABLES = dataclasses.field(
        default_factory=dict
    )

    @classmethod
    def from_document(
        cls,
        doc: "ResourceTypeDocument",
        ars: "ARS",
    ):
        """
        For example: if the doc is::

            {"id": "s3-bucket", "name": "s3-bucket"}

        Then the item will be::

            {
                "title": "s3-bucket",
                "subtitle": "hit 'Tab' and enter your query to search.",
                "uid": "s3-bucket",
                "arg": "s3-bucket",
                "autocomplete": "s3-bucket: ",
            }
        """
        resource_type = doc.name
        desc = doc.desc
        searcher = ars.searcher_finder.import_searcher(resource_type)
        try:
            console_url = searcher.doc_class.get_list_resources_console_url(
                console=ars.aws_console
            )
            subtitle = (
                f"hit {ShortcutEnum.TAB} to search, "
                f"hit {ShortcutEnum.ENTER} to list resources in AWS console."
            )
        except NotImplementedError:
            console_url = None
            subtitle = f"hit {ShortcutEnum.TAB} to search"
        return cls(
            title=f"{format_resource_type(resource_type)}: {desc}",
            subtitle=subtitle,
            uid=doc.id,
            arg=resource_type,
            autocomplete=resource_type + ": ",
            variables={
                "doc": doc,
                "resource_type": resource_type,
                "console_url": console_url,
            },
        )

    @classmethod
    def from_many_document(
        cls,
        docs: T.Iterable["ResourceTypeDocument"],
        ars: "ARS",
    ):
        return [cls.from_document(doc, ars) for doc in docs]

    def enter_handler(self, ui: "UI"):  # pragma: no cover
        """
        Behavior:

        For resource type search, when user hit "Enter", it opens the
        AWS console to list resources of this type.
        """
        if self.variables.get("console_url"):
            self.open_url_or_print(ui, self.variables["console_url"])

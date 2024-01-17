# -*- coding: utf-8 -*-

"""
todo: docstring
"""

import typing as T
import dataclasses

from ..terminal import ShortcutEnum, format_resource_type
from ..compat import TypedDict
from ..searcher_finder import searcher_finder

from .base_item import BaseArsItem

if T.TYPE_CHECKING:  # pragma: no cover
    from ..documents.resource_document import T_ARS_RESOURCE_DOCUMENT
    from ..ars import ARS
    from ..ui.main import UI


@dataclasses.dataclass
class T_AWS_RESOURCE_ITEM_VARIABLES(TypedDict):
    """
    Type hint for the "variables" field in :class:`AwsResourceItem`.
    """
    doc: T_ARS_RESOURCE_DOCUMENT
    resource_type: str
    partitioner_resource_type: T.Optional[str]


@dataclasses.dataclass
class AwsResourceItem(BaseArsItem):
    """
    Represent an item in the resource search result.

    :param variables: in AwsResourceItem, the variable is a dictionary including
        the original document object (not dict).
    """

    variables: T_AWS_RESOURCE_ITEM_VARIABLES = dataclasses.field(default_factory=dict)

    @classmethod
    def from_document(
        cls,
        resource_type: str,
        doc: "T_ARS_RESOURCE_DOCUMENT",
    ):
        """
        A factory method that convert a dictionary view of a
        :class:`~aws_resource_search.documents.resource_document.ResourceDocument`
        object to an :class:`AwsResourceItem`.

        For example: if the doc is::

            >>> doc = dataclasses.asdict(
            ...     S3Bucket(
            ...         title="my-bucket",
            ...         subtitle="bucket creation date",
            ...         uid="my-bucket",
            ...         autocomplete="my-bucket",
            ...     )
            ... )

        Then the item will be::

            >>> dataclasses.asdict(AwsResourceItem.from_document(doc))
            {
                "title": "my-bucket",
                "subtitle": "bucket creation date",
                "uid": "s3-bucket",
                "autocomplete": "s3-bucket: my-bucket",
                "variables": {"doc": S3Bucket(...)},
            }

        We also have an array version :meth:`AwsResourceItem.from_many_document`.
        """
        return cls(
            title=doc.title,
            subtitle=doc.subtitle,
            uid=doc.uid,
            autocomplete=f"{resource_type}: {doc.autocomplete}",
            variables={
                "doc": doc,
                "resource_type": resource_type,
                "partitioner_resource_type": None,
            },
        )

    @classmethod
    def from_many_document(
        cls,
        resource_type: str,
        docs: T.Iterable["T_ARS_RESOURCE_DOCUMENT"],
    ):
        """
        An array version of :meth:`AwsResourceItem.from_document`.
        """
        return [cls.from_document(resource_type, doc) for doc in docs]

    def get_id(self) -> str:
        """
        Get the resource id.
        """
        return self.variables["doc"].id

    def get_name(self) -> str:
        """
        Get the resource name.
        """
        return self.variables["doc"].name

    def get_console_url(self) -> str:
        """
        Get AWS console url of the resource.
        """
        doc: "T_ARS_RESOURCE_DOCUMENT" = self.variables["doc"]
        return doc.console_url

    def get_arn(self) -> str:
        """
        Get ARN of the resource.
        """
        return self.variables["doc"].arn

    def enter_handler(self, ui: "UI"):
        """
        Default behavior:

        Open AWS console url in browser.
        """
        self.open_url_or_print(ui, self.get_console_url())

    def ctrl_a_handler(self, ui: "UI"):
        """
        Default behavior:

        Copy ARN to clipboard.
        """
        self.copy_or_print(ui, self.get_arn())

    def ctrl_u_handler(self, ui: "UI"):
        """
        Default behavior:

        Copy AWS console url to clipboard.
        """
        self.copy_or_print(ui, self.get_console_url())

    def ctrl_p_handler(self, ui: "UI"):
        """
        View details in a sub session. You can tap 'F1' to exit the sub session.
        """
        doc: "T_ARS_RESOURCE_DOCUMENT" = self.variables["doc"]
        items = doc.get_details(ars=ars)
        ui.run_handler(items=items)

        # enter the main event loop of the sub query
        # user can tap 'F1' to exit the sub query session,
        # and go back to the folder selection session.
        def handler(query: str, ui: "UI"):
            """
            A partial function that using the given folder.
            """
            ui.render.prompt = "(Detail)"
            return items

        ui.run_sub_session(
            handler=handler,
            initial_query=(
                f"{ui.remove_text_format(self.title)}, " f"press F1 to go back."
            ),
        )
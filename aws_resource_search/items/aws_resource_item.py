# -*- coding: utf-8 -*-

"""
See :class:`AwsResourceItem`.
"""

import typing as T
import dataclasses

from ..compat import TypedDict
from ..terminal import remove_text_format

from .base_item import BaseArsItem

if T.TYPE_CHECKING:  # pragma: no cover
    import aws_console_url.api as acu

    from ..documents.resource_document import T_ARS_RESOURCE_DOCUMENT
    from ..ui_def import UI


@dataclasses.dataclass
class T_AWS_RESOURCE_ITEM_VARIABLES(TypedDict):
    """
    Type hint for the "variables" field in :class:`AwsResourceItem`.
    """

    doc: "T_ARS_RESOURCE_DOCUMENT"
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

    def get_console_url(self, console: "acu.AWSConsole") -> str:
        """
        Get AWS console url of the resource.
        """
        doc: "T_ARS_RESOURCE_DOCUMENT" = self.variables["doc"]
        return doc.get_console_url(console=console)

    def get_arn(self) -> str:
        """
        Get ARN of the resource.
        """
        return self.variables["doc"].arn

    def enter_handler(self, ui: "UI"):  # pragma: no cover
        """
        Default behavior:

        Open AWS console url in browser.
        """
        self.open_url_or_print(ui, self.get_console_url(console=ui.ars.aws_console))

    def ctrl_a_handler(self, ui: "UI"):  # pragma: no cover
        """
        Default behavior:

        Copy ARN to clipboard.
        """
        self.copy_or_print(ui, self.get_arn())

    def ctrl_u_handler(self, ui: "UI"):  # pragma: no cover
        """
        Default behavior:

        Copy AWS console url to clipboard.
        """
        self.copy_or_print(ui, self.get_console_url(console=ui.ars.aws_console))

    def ctrl_p_handler(self, ui: "UI"):  # pragma: no cover
        """
        View details in a sub session. You can tap 'F1' to exit the sub session.
        """
        doc: "T_ARS_RESOURCE_DOCUMENT" = self.variables["doc"]
        items = doc.get_details(ars=ui.ars)
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
                f"{remove_text_format(self.title)}, " f"press F1 to go back."
            ),
        )

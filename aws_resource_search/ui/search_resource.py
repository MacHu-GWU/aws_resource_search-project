# -*- coding: utf-8 -*-

"""
This module implements the resource search feature.
"""

import typing as T
import dataclasses

import zelfred.api as zf

try:
    import pyperclip
except ImportError:
    pass

from .search_patterns import (
    has_partitioner,
    get_partitioner_resource_type,
    get_partitioner_boto_kwargs,
)
from ..res_lib import T_DOCUMENT_OBJ, preprocess_query, Searcher
from .common import repaint_ui
from .boto_ses import bsm, ars


class TVariables(T.TypedDict):
    doc: T_DOCUMENT_OBJ


@dataclasses.dataclass
class AwsResourceItem(zf.Item):
    """
    Represent an item in the resource search result.

    :param variables: it has the original document object.
    """

    variables: TVariables = dataclasses.field(default_factory=dict)

    @classmethod
    def from_document(
        cls,
        resource_type: str,
        doc: T_DOCUMENT_OBJ,
    ):
        """
        For example: if the doc is::

            S3Bucket(
                title="my-bucket",
                subtitle="bucket creation date",
                uid="my-bucket",
                autocomplete="my-bucket",
            )

        Then the item will be::

            {
                "title": "my-bucket",
                "subtitle": "bucket creation date",
                "uid": "s3-bucket",
                "autocomplete": "s3-bucket: my-bucket",
                "variables": {"doc": S3Bucket(...)},
            }
        """
        return cls(
            title=doc.title,
            subtitle=doc.subtitle,
            uid=doc.uid,
            autocomplete=f"{resource_type}: {doc.autocomplete}",
            variables={"doc": doc},
        )

    @classmethod
    def from_many_document(
        cls,
        resource_type: str,
        docs: T.Iterable[T_DOCUMENT_OBJ],
    ):
        return [cls.from_document(resource_type, doc) for doc in docs]

    def enter_handler(self, ui: zf.UI):
        """
        open AWS console url in browser
        """
        doc: T_DOCUMENT_OBJ = self.variables["doc"]
        try:
            console_url = doc.get_console_url(ars.aws_console)
            zf.open_url(console_url)
        except NotImplementedError:
            raise NotImplementedError(
                f"{doc.__class__.__name__} doesn't support console url"
            )

    def ctrl_a_handler(self, ui: zf.UI):
        """
        Copy ARN to clipboard.
        """
        doc: T_DOCUMENT_OBJ = self.variables["doc"]
        try:
            arn = self.variables["doc"].arn
            pyperclip.copy(arn)
        except NotImplementedError:
            raise NotImplementedError(f"{doc.__class__.__name__} doesn't support ARN")

    def ctrl_p_handler(self, ui: zf.UI):
        """
        View details in a sub session. You can tap 'F1' to exit the sub session.
        """
        doc: T_DOCUMENT_OBJ = self.variables["doc"]
        try:
            items = doc.details()
            ui.run_handler(items=items)

            # enter the main event loop of the sub query
            # user can tap 'F1' to exit the sub query session,
            # and go back to the folder selection session.
            def handler(query: str, ui: zf.UI):
                """
                A partial function that using the given folder.
                """
                return items

            ui.replace_handler(handler)

            # re-paint the UI
            ui.line_editor.clear_line()
            repaint_ui(ui)
            ui.run(_do_init=False)
        except NotImplementedError:
            raise NotImplementedError(f"{doc.__class__.__name__} doesn't support ARN")


def creating_index_items(resource_type: str) -> T.List[zf.Item]:
    """
    Print a message to tell user that we are creating index.

    This method is used when we need to create or recreate the index.
    """
    return [
        zf.Item(
            uid="uid",
            title=f"Pulling data for {resource_type!r}, it may takes 1-60 seconds ...",
            subtitle="please wait, don't press any key",
        )
    ]


T_DOC_TO_ITEM_FUNC = T.Callable[[T_DOCUMENT_OBJ], AwsResourceItem]


def search_resource_and_return_items(
    searcher: Searcher,
    query: str,
    boto_kwargs: T.Optional[dict] = None,
    refresh_data: bool = False,
    doc_to_item_func: T_DOC_TO_ITEM_FUNC = None,
) -> T.List[AwsResourceItem]:
    """
    A wrapper of the :class:`~aws_resource_search.res_lib.Searcher`.
    It will return a list of UI items instead of a list of documents.

    :param searcher: corresponding resource type searcher object.
    :param query: example "my bucket", "my role".
    :param boto_kwargs: additional boto3 kwargs.
    :param refresh_data: do we need to refresh the data?
    :param doc_to_item_func: a callable function that convert document object
        to zelfred Item object. For those resources don't have mandatory
        arguments for boto3 API, it is very simple. But for those resources
        need a parent resource name as an argument for the boto3 API,
        we need special handling to convert the original doc to item.
        That's the purpose of this argument.
    """
    docs: T.List[T_DOCUMENT_OBJ] = searcher.search(
        query=query,
        boto_kwargs=boto_kwargs,
        refresh_data=refresh_data,
    )
    # pprint(docs[:3]) # for DEBUG ONLY

    if doc_to_item_func is None:

        def doc_to_item_func(doc: T_DOCUMENT_OBJ) -> AwsResourceItem:
            return AwsResourceItem.from_document(
                resource_type=searcher.resource_type,
                doc=doc,
            )

    items = [doc_to_item_func(doc=doc) for doc in docs]
    # pprint(items[:3]) # for DEBUG ONLY
    return items


def search_resource(
    ui: zf.UI,
    resource_type: str,
    query: str,
    boto_kwargs: T.Optional[dict] = None,
    doc_to_item_func: T_DOC_TO_ITEM_FUNC = None,
) -> T.List[AwsResourceItem]:
    """
    **IMPORTANT** this is the sub logic to handle AWS resource that doesn't have
    any mandatory boto kwargs. This is the MOST common case.

    A wrapper around :func:`search_and_return_items`, it also handles the case
    that we have to create the index and the case that user wants to refresh data.

    :param query: example "my bucket", "my role"
    :param doc_to_item_func: a callable function that convert document object
        to zelfred Item object.
    """
    zf.debugger.log(f"search_resource Query: {query}")
    final_query = preprocess_query(query)
    searcher = ars.get_searcher(resource_type)
    ds = searcher._get_ds(bsm=bsm, final_boto_kwargs={})

    # display "creating index ..." message
    if ds.cache_key not in ds.cache:
        ui.run_handler(items=creating_index_items(resource_type))
        repaint_ui(ui)
        return search_resource_and_return_items(
            searcher=searcher,
            query=final_query,
            boto_kwargs=boto_kwargs,
            doc_to_item_func=doc_to_item_func,
        )

    # manually refresh data
    if final_query.endswith("!~"):
        ui.run_handler(items=creating_index_items(resource_type))
        repaint_ui(ui)
        ui.line_editor.press_backspace(n=2)
        return search_resource_and_return_items(
            searcher=searcher,
            query=preprocess_query(final_query[:-2]),
            boto_kwargs=boto_kwargs,
            refresh_data=True,
            doc_to_item_func=doc_to_item_func,
        )

    # example: "ec2-inst: dev box"
    return search_resource_and_return_items(
        searcher=searcher,
        query=final_query,
        doc_to_item_func=doc_to_item_func,
    )


def search_partitioner(
    ui: zf.UI,
    resource_type: str,
    partitioner_resource_type: str,
    partitioner_query: str,
) -> T.List[AwsResourceItem]:
    """
    Search partitioner resource.

    A wrapper of the :class:`~aws_resource_search.res_lib.Searcher`.
    It assumes that you have to search another resource before searching the
    real resource. For example, you have to search glue database before you can
    search glue table, since glue table boto3 API call requires the glue database.
    In this example, the glue_table is the searcher, and the glue_database is the
    partitioner_searcher. It returns a list of UI items instead of a list of documents.

    :param query: example: "my database"
    """
    zf.debugger.log(f"search_partitioner Query: {partitioner_query!r}")

    def doc_to_item_func(doc: T_DOCUMENT_OBJ) -> AwsResourceItem:
        return AwsResourceItem(
            uid=doc.uid,
            title=f"{partitioner_resource_type}: {doc.title}",
            subtitle=f"Tap 'Tab' to search {resource_type} in this {partitioner_resource_type}",
            autocomplete=f"{resource_type}: {doc.autocomplete}@",
            variables={"doc": doc},
        )

    return search_resource(
        ui=ui,
        resource_type=partitioner_resource_type,
        query=partitioner_query,
        doc_to_item_func=doc_to_item_func,
    )


def search_child_resource(
    ui: zf.UI,
    resource_type: str,
    resource_query: str,
    partitioner_query: str,
    boto_kwargs: T.Dict[str, T.Any],
) -> T.List[AwsResourceItem]:
    """
    Search child resource under the given partitioner.

    A wrapper of the :class:`~aws_resource_search.res_lib.Searcher`. But it will
    return a list of UI items instead of a list of documents.

    :param resource_type: example: "glue-table"
    :param partitioner_resource_type: example: "glue-database"
    :param resource_query: example: "my table"
    :param partitioner_query: example: "my database"
    """
    zf.debugger.log(f"search_child_resource Partitioner Query: {partitioner_query!r}")
    zf.debugger.log(f"search_child_resource Child Query: {resource_query!r}")

    def doc_to_item_func(doc: T_DOCUMENT_OBJ) -> AwsResourceItem:
        return AwsResourceItem(
            uid=doc.uid,
            title=f"{resource_type}: {doc.title}",
            subtitle=doc.subtitle,
            autocomplete=f"{resource_type}: {doc.autocomplete}",
            variables={"doc": doc},
        )

    return search_resource(
        ui=ui,
        resource_type=resource_type,
        query=resource_query,
        boto_kwargs=boto_kwargs,
        doc_to_item_func=doc_to_item_func,
    )


def search_resource_under_partitioner(
    ui: zf.UI,
    resource_type: str,
    partitioner_resource_type: str,
    query: str,
):
    """
    **IMPORTANT** this is the sub logic to handle AWS resource like glue table,
    glue job run, that requires the parent resource name in the arguments.

    :param resource_type: for example, ``"glue-table"``
    :param partitioner_resource_type: for example, ``"glue-database"``
    :param query: for example, if the full user query is ``"glue-table: my_database@my table"``,
        then this argument is ``"my_database@my table"``.
    """
    zf.debugger.log(f"search_resource_under_partitioner Query: {query}")
    q = zf.QueryParser(delimiter="@").parse(query)
    # --- search partitioner
    # examples
    # - "  "
    # - "my database"

    # example: " "
    if len(q.trimmed_parts) == 0:
        return search_partitioner(
            resource_type=resource_type,
            partitioner_resource_type=partitioner_resource_type,
            partitioner_query="*",
            ui=ui,
        )
    # example: "my database "
    elif len(q.trimmed_parts) == 1 and len(q.parts) == 1:
        return search_partitioner(
            resource_type=resource_type,
            partitioner_resource_type=partitioner_resource_type,
            partitioner_query=q.trimmed_parts[0],
            ui=ui,
        )
    else:
        pass

    # --- search resource
    # examples
    # - "my_database@"
    # - "my_database@my table"
    partitioner_query = q.trimmed_parts[0]
    boto_kwargs = get_partitioner_boto_kwargs(resource_type, partitioner_query)

    # example: "my_database@  "
    if len(q.trimmed_parts) == 1 and len(q.parts) > 1:
        return search_child_resource(
            ui=ui,
            resource_type=resource_type,
            resource_query="*",
            partitioner_query=partitioner_query,
            boto_kwargs=boto_kwargs,
        )
    # i.e. len(q.trimmed_parts) > 1
    # example: "my_database@my table"
    else:
        resource_query = query.split("@", 1)[1].strip()
        return search_child_resource(
            ui=ui,
            resource_type=resource_type,
            resource_query=resource_query,
            partitioner_query=partitioner_query,
            boto_kwargs=boto_kwargs,
        )


def search_resource_handler(
    resource_type: str,
    query: str,
    ui: zf.UI,
) -> T.List[AwsResourceItem]:
    """
    **IMPORTANT** This handle filter resource by query.

    :param resource_type: for example, ``"s3-bucket"``
    :param query: for example, if the full user query is ``"s3-bucket: my bucket"``,
        then this argument is ``"my bucket"``.
    """
    if has_partitioner(resource_type):
        return search_resource_under_partitioner(
            ui=ui,
            resource_type=resource_type,
            partitioner_resource_type=get_partitioner_resource_type(resource_type),
            query=query,
        )
    else:
        return search_resource(
            ui=ui,
            resource_type=resource_type,
            query=query,
        )
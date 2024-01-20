# -*- coding: utf-8 -*-

"""
See :func:`select_resource_handler`.
"""

import typing as T

import botocore.exceptions
import zelfred.api as zf

from ..paths import path_aws_config, path_aws_credentials
from .. import res_lib as rl


if T.TYPE_CHECKING:  # pragma: no cover
    from ..ui_def import UI


def creating_index_items(resource_type: str) -> T.List[rl.InfoItem]:  # pragma: no cover
    """
    Print a message to tell user that we are creating index.

    This method is used when we need to create or recreate the index.
    """
    return [
        rl.InfoItem(
            title=f"Pulling data for {resource_type!r}, it may takes 1-60 seconds ...",
            subtitle="please wait, don't press any key",
            uid="pulling-data",
        )
    ]


T_DOC_TO_ITEM_FUNC = T.Callable[[rl.T_ARS_RESOURCE_DOCUMENT], rl.AwsResourceItem]


def search_resource_and_return_items(
    ui: "UI",
    searcher: rl.T_SEARCHER,
    query: str,
    boto_kwargs: T.Optional[dict] = None,
    refresh_data: bool = False,
    doc_to_item_func: T_DOC_TO_ITEM_FUNC = None,
    skip_ui: bool = False,
) -> T.List[T.Union[rl.AwsResourceItem, rl.InfoItem, rl.FileItem]]:
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
    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    try:
        docs: T.List[rl.T_ARS_RESOURCE_DOCUMENT] = searcher.search(
            query=query,
            boto_kwargs=boto_kwargs,
            refresh_data=refresh_data,
        )
    except botocore.exceptions.ClientError as e:  # pragma: no cover
        return [
            rl.InfoItem(
                title=(
                    f"🔴 boto3 client error! "
                    f"check your default profile in ~/.aws/config and ~/.aws/credentials file."
                ),
                subtitle=repr(e),
                uid="boto3-client-error",
            ),
            rl.FileItem(
                title=f"Check ~/.aws/config",
                subtitle=f"{rl.ShortcutEnum.ENTER} to open file",
                arg=str(path_aws_config),
                uid="open-aws-config",
            ),
            rl.FileItem(
                title=f"Check ~/.aws/credentials",
                subtitle=f"{rl.ShortcutEnum.ENTER} to open file",
                arg=str(path_aws_credentials),
            ),
        ]

    # pprint(docs[:3]) # for DEBUG ONLY

    if doc_to_item_func is None:

        def doc_to_item_func(doc: rl.T_ARS_RESOURCE_DOCUMENT) -> rl.AwsResourceItem:
            return rl.AwsResourceItem.from_document(
                resource_type=searcher.resource_type,
                doc=doc,
            )

    items = [doc_to_item_func(doc=doc) for doc in docs]
    # pprint(items[:3]) # for DEBUG ONLY
    if len(items):
        return items
    else:
        # display helper text to tell user that we can't find any resource
        line = ui.line_editor.line
        if "@" in line:  # cannot find any sub resource
            autocomplete = line.split("@", 1)[0] + "@"
        else:  # cannot find resource
            autocomplete = line.split(":", 1)[0] + ": "
        return [
            rl.InfoItem(
                title=f"🔴 No {searcher.resource_type!r} found",
                subtitle=(
                    "Please try another query, "
                    "or type {} to refresh data, "
                    "or tap {} to clear existing query."
                ).format(
                    rl.highlight_text("!~"),
                    rl.ShortcutEnum.TAB,
                ),
                autocomplete=autocomplete,
            )
        ]


def search_resource(
    ui: "UI",
    resource_type: str,
    query: str,
    boto_kwargs: T.Optional[dict] = None,
    doc_to_item_func: T_DOC_TO_ITEM_FUNC = None,
    skip_ui: bool = False,
) -> T.List[T.Union[rl.AwsResourceItem, rl.InfoItem, rl.FileItem]]:
    """
    A wrapper around :func:`search_and_return_items`, it also handles the case
    that we have to create the index and the case that user wants to refresh data.

    .. note::

        this is the sub logic to handle AWS resource that doesn't have
        any mandatory boto kwargs. This is the MOST common case.

    :param ui: UI object.
    :param resource_type: the resource type name
    :param query: example "my bucket", "my role"
    :param doc_to_item_func: a callable function that convert document object
        to zelfred Item object.
    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    zf.debugger.log(f"search_resource Query: {query}")
    final_query = rl.preprocess_query(query)
    searcher = ui.ars.get_searcher(resource_type)
    final_boto_kwargs = searcher._get_final_boto_kwargs(boto_kwargs=boto_kwargs)
    ds = searcher._get_ds(bsm=ui.ars.bsm, final_boto_kwargs=final_boto_kwargs)

    # display "creating index ..." message
    if ds.cache_key not in ds.cache:
        if skip_ui is False:  # pragma: no cover
            ui.run_handler(items=creating_index_items(resource_type))
            ui.repaint()
        return search_resource_and_return_items(
            ui=ui,
            searcher=searcher,
            query=final_query,
            boto_kwargs=boto_kwargs,
            doc_to_item_func=doc_to_item_func,
            skip_ui=skip_ui,
        )

    # manually refresh data
    if final_query.endswith("!~"):
        if skip_ui is False:  # pragma: no cover
            ui.run_handler(items=creating_index_items(resource_type))
            ui.repaint()
            ui.line_editor.press_backspace(n=2)
        return search_resource_and_return_items(
            ui=ui,
            searcher=searcher,
            query=rl.preprocess_query(final_query[:-2]),
            boto_kwargs=boto_kwargs,
            refresh_data=True,
            doc_to_item_func=doc_to_item_func,
            skip_ui=skip_ui,
        )

    # example: "ec2-inst: dev box"
    return search_resource_and_return_items(
        ui=ui,
        searcher=searcher,
        query=final_query,
        boto_kwargs=boto_kwargs,
        doc_to_item_func=doc_to_item_func,
        skip_ui=skip_ui,
    )


def search_partitioner(
    ui: "UI",
    resource_type: str,
    partitioner_resource_type: str,
    partitioner_query: str,
    skip_ui: bool = False,
) -> T.List[T.Union[rl.AwsResourceItem, rl.InfoItem, rl.FileItem]]:
    """
    Search partitioner resource.

    A wrapper of the :class:`~aws_resource_search.base_searcher.BaseSearcher`.
    It assumes that you have to search another resource before searching the
    real resource. For example, you have to search glue database before you can
    search glue table, since glue table boto3 API call requires the glue database.
    In this example, the glue_table is the searcher, and the glue_database is the
    partitioner_searcher. It returns a list of UI items instead of a list of documents.

    :param ui: UI object.
    :param resource_type: the resource type name
    :param partitioner_resource_type: the partitioner (parent) resource type name
    :param partitioner_query: the query to filter partitioner, example: "sfn state machine"
    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    zf.debugger.log(f"search_partitioner Query: {partitioner_query!r}")

    def doc_to_item_func(doc: rl.T_ARS_RESOURCE_DOCUMENT) -> rl.AwsResourceItem:
        return rl.AwsResourceItem(
            uid=doc.uid,
            # title=f"{format_resource_type(partitioner_resource_type)}: {format_value(doc.autocomplete)}",
            title=f"{rl.format_resource_type(partitioner_resource_type)}: {doc.title}",
            subtitle=(
                f"Tap {rl.ShortcutEnum.TAB} "
                f"to search {rl.format_resource_type(resource_type)} "
                f"in this {rl.format_resource_type(partitioner_resource_type)}, "
                f"Tap {rl.ShortcutEnum.ENTER} to open {rl.format_resource_type(partitioner_resource_type)} url."
            ),
            autocomplete=f"{resource_type}: {doc.autocomplete}@",
            variables={
                "doc": doc,
                "resource_type": resource_type,
                "partitioner_resource_type": partitioner_resource_type,
            },
        )

    return search_resource(
        ui=ui,
        resource_type=partitioner_resource_type,
        query=partitioner_query,
        doc_to_item_func=doc_to_item_func,
        skip_ui=skip_ui,
    )


def search_child_resource(
    ui: "UI",
    resource_type: str,
    partitioner_resource_type: str,
    resource_query: str,
    partitioner_query: str,
    boto_kwargs: T.Dict[str, T.Any],
    skip_ui: bool = False,
) -> T.List[T.Union[rl.AwsResourceItem, rl.InfoItem, rl.FileItem]]:
    """
    Search child resource under the given partitioner.

    A wrapper of the :class:`~aws_resource_search.res_lib.Searcher`. But it will
    return a list of UI items instead of a list of documents.

    :param ui: UI object.
    :param resource_type: example: "glue-database-table"
    :param partitioner_resource_type: example: "glue-database"
    :param resource_query: example: "my table"
    :param partitioner_query: example: "my database"
    :param boto_kwargs: example: {"database_name": "my database"},
        for searching glue table under the given database
    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    zf.debugger.log(f"search_child_resource Partitioner Query: {partitioner_query!r}")
    zf.debugger.log(f"search_child_resource Child Query: {resource_query!r}")

    def doc_to_item_func(doc: rl.T_ARS_RESOURCE_DOCUMENT) -> rl.AwsResourceItem:
        return rl.AwsResourceItem(
            uid=doc.uid,
            title=f"{rl.format_resource_type(resource_type)}: {doc.title}",
            subtitle=doc.subtitle,
            autocomplete=f"{resource_type}: {doc.autocomplete}",
            variables={
                "doc": doc,
                "resource_type": resource_type,
                "partitioner_resource_type": partitioner_resource_type,
            },
        )

    return search_resource(
        ui=ui,
        resource_type=resource_type,
        query=resource_query,
        boto_kwargs=boto_kwargs,
        doc_to_item_func=doc_to_item_func,
        skip_ui=skip_ui,
    )


def search_resource_under_partitioner(
    ui: "UI",
    resource_type: str,
    partitioner_resource_type: str,
    query: str,
    skip_ui: bool = False,
) -> T.List[T.Union[rl.AwsResourceItem, rl.InfoItem, rl.FileItem]]:
    """
    **IMPORTANT** this is the sub logic to handle AWS resource like glue table,
    glue job run, that requires the parent resource name in the arguments.

    :param resource_type: for example, ``"glue-table"``
    :param partitioner_resource_type: for example, ``"glue-database"``
    :param query: for example, if the full user query is ``"glue-table: my_database@my table"``,
        then this argument is ``"my_database@my table"``.
    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    zf.debugger.log(f"search_resource_under_partitioner Query: {query}")
    q = zf.QueryParser(delimiter="@").parse(query)
    # --- search partitioner
    # for parent resource like glue job for glue job run, state machine for step function execution
    #
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
            skip_ui=skip_ui,
        )
    # example: "my database "
    elif len(q.trimmed_parts) == 1 and len(q.parts) == 1:
        return search_partitioner(
            resource_type=resource_type,
            partitioner_resource_type=partitioner_resource_type,
            partitioner_query=q.trimmed_parts[0],
            ui=ui,
            skip_ui=skip_ui,
        )
    else:
        pass

    # --- search child resource
    # examples
    # - "my_database@"
    # - "my_database@my table"
    partitioner_query = q.trimmed_parts[0]
    boto_kwargs = ui.ars.get_partitioner_boto_kwargs(resource_type, partitioner_query)

    # example: "my_database@  "
    if len(q.trimmed_parts) == 1 and len(q.parts) > 1:
        return search_child_resource(
            ui=ui,
            resource_type=resource_type,
            partitioner_resource_type=partitioner_resource_type,
            resource_query="*",
            partitioner_query=partitioner_query,
            boto_kwargs=boto_kwargs,
            skip_ui=skip_ui,
        )
    # i.e. len(q.trimmed_parts) > 1
    # example: "my_database@my table"
    else:
        resource_query = query.split("@", 1)[1].strip()
        return search_child_resource(
            ui=ui,
            resource_type=resource_type,
            partitioner_resource_type=partitioner_resource_type,
            resource_query=resource_query,
            partitioner_query=partitioner_query,
            boto_kwargs=boto_kwargs,
            skip_ui=skip_ui,
        )


def search_resource_handler(
    ui: "UI",
    resource_type: str,
    query: str,
    skip_ui: bool = False,
) -> T.List[T.Union[rl.AwsResourceItem, rl.InfoItem, rl.FileItem]]:  # pragma: no cover
    """
    **IMPORTANT** This handle filter resource by query.

    :param resource_type: for example, ``"s3-bucket"``
    :param query: for example, if the full user query is ``"s3-bucket: my bucket"``,
        then this argument is ``"my bucket"``.
    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    ui.render.prompt = f"(Query)"
    if ui.ars.has_partitioner(resource_type):
        return search_resource_under_partitioner(
            ui=ui,
            resource_type=resource_type,
            partitioner_resource_type=ui.ars.get_partitioner_resource_type(resource_type),
            query=query,
            skip_ui=skip_ui,
        )
    else:
        return search_resource(
            ui=ui,
            resource_type=resource_type,
            query=query,
            skip_ui=skip_ui,
        )

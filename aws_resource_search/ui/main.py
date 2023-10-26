# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import zelfred.api as zf
from boto_session_manager import BotoSesManager

try:
    import pyperclip
except ImportError:
    pass

from ..ars_v2 import ARS
from ..searchers import searchers_metadata, SearcherEnum
from ..res_lib import T_DOCUMENT_OBJ, preprocess_query, Searcher
from .search_resource_type import (
    AwsResourceTypeItem,
    select_resource_type_handler,
)

bsm = BotoSesManager()
ars = ARS(bsm=bsm)


class TVariables(T.TypedDict):
    doc: T_DOCUMENT_OBJ


@dataclasses.dataclass
class AwsResourceItem(zf.Item):
    variables: TVariables = dataclasses.field(default_factory=dict)

    @classmethod
    def from_document(cls, resource_type: str, doc: T_DOCUMENT_OBJ):
        return cls(
            uid=doc.uid,
            title=doc.title,
            subtitle=doc.subtitle,
            autocomplete=f"{resource_type}: {doc.autocomplete}",
            variables={"doc": doc},
        )

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
        View details.
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


def search_and_return_items(
    searcher: Searcher,
    query: str,
    boto_kwargs: T.Optional[dict] = None,
    refresh_data: bool = False,
    doc_to_item_func: T_DOC_TO_ITEM_FUNC = None,
) -> T.List[AwsResourceItem]:
    """
    A wrapper of the :class:`~aws_resource_search.res_lib.Searcher`.
    It assumes that there's no boto_kwargs needed for the searcher.
    It will return a list of UI items instead of a list of documents.

    :param query: example "my bucket", "my role"
    :param doc_to_item_func: a callable function that convert document object
        to zelfred Item object.
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


def repaint_ui(ui: zf.UI):
    """
    Repaint the UI right after the items is ready. This is useful when you want
    to show a message before running the real handler.
    """
    # you should handle the ``ui.run_handler()`` logic yourself
    ui.move_to_end()
    ui.clear_items()
    ui.clear_query()
    ui.print_query()
    ui.print_items()


def search_resource_handler_may_has_kwargs(
    ui: zf.UI,
    resource_type: str,
    query: str,
    boto_kwargs: T.Optional[dict] = None,
    doc_to_item_func: T_DOC_TO_ITEM_FUNC = None,
):
    """
    **IMPORTANT** this is the sub logic to handle AWS resource that doesn't have
    any mandatory boto kwargs.

    A wrapper around :func:`search_and_return_items`, it also handles the case
    that we have to create the index and the case that user wants to refresh data.

    :param query: example "my bucket", "my role"
    :param doc_to_item_func: a callable function that convert document object
        to zelfred Item object.
    """
    zf.debugger.log(f"search_resource_handler_no_kwargs Query: {query}")
    final_query = preprocess_query(query)
    searcher = ars._get_searcher(resource_type)
    ds = searcher._get_ds(bsm=bsm, final_boto_kwargs={})

    # display "creating index ..." message
    if ds.cache_key not in ds.cache:
        ui.run_handler(items=creating_index_items(resource_type))
        repaint_ui(ui)
        return search_and_return_items(
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
        return search_and_return_items(
            searcher=searcher,
            query=preprocess_query(final_query[:-2]),
            boto_kwargs=boto_kwargs,
            refresh_data=True,
            doc_to_item_func=doc_to_item_func,
        )

    # example: "ec2-inst: dev box"
    return search_and_return_items(
        searcher=searcher,
        query=final_query,
        doc_to_item_func=doc_to_item_func,
    )


def search_partitioner_handler(
    resource_type: str,
    partitioner_resource_type: str,
    partitioner_query: str,
    ui: zf.UI,
) -> T.List[AwsResourceItem]:
    """
    A wrapper of the :class:`~aws_resource_search.res_lib.Searcher`.
    It assumes that you have to search another resource before searching the
    real resource. For example, you have to search glue database before you can
    search glue table, since glue table boto3 API call requires the glue database.
    In this example, the glue_table is the searcher, and the glue_database is the
    partitioner_searcher. It returns a list of UI items instead of a list of documents.

    :param query: example: "my database"
    """
    zf.debugger.log(
        f"search_partitioner_handler_no_kwargs Query: {partitioner_query!r}"
    )

    def doc_to_item_func(doc: T_DOCUMENT_OBJ) -> AwsResourceItem:
        return AwsResourceItem(
            uid=doc.uid,
            title=f"{partitioner_resource_type}: {doc.title}",
            subtitle=f"Tap 'Tab' to search {resource_type} in this {partitioner_resource_type}",
            autocomplete=f"{resource_type}: {doc.autocomplete}@",
            variables={"doc": doc},
        )

    return search_resource_handler_may_has_kwargs(
        resource_type=partitioner_resource_type,
        query=partitioner_query,
        ui=ui,
        doc_to_item_func=doc_to_item_func,
    )


def search_resource_under_partitioner_handler(
    ui: zf.UI,
    resource_type: str,
    resource_query: str,
    partitioner_query: str,
    boto_kwargs: T.Dict[str, T.Any],
) -> T.List[AwsResourceItem]:
    """
    A wrapper of the :class:`~aws_resource_search.res_lib.Searcher`. But it will
    return a list of UI items instead of a list of documents.

    :param resource_type: example: "glue-table"
    :param partitioner_resource_type: example: "glue-database"
    :param resource_query: example: "my table"
    :param partitioner_query: example: "my database"
    """
    zf.debugger.log(
        f"search_resource_under_partitioner_handler Partitioner Query: {partitioner_query!r}"
    )
    zf.debugger.log(
        f"search_resource_under_partitioner_handler Resource Query: {resource_query!r}"
    )

    def doc_to_item_func(doc: T_DOCUMENT_OBJ) -> AwsResourceItem:
        return AwsResourceItem(
            uid=doc.uid,
            title=f"{resource_type}: {doc.title}",
            subtitle=doc.subtitle,
            autocomplete=f"{resource_type}: {doc.autocomplete}",
            variables={"doc": doc},
        )

    return search_resource_handler_may_has_kwargs(
        ui=ui,
        resource_type=resource_type,
        query=resource_query,
        boto_kwargs=boto_kwargs,
        doc_to_item_func=doc_to_item_func,
    )


def search_resource_handler_has_partitioner(
    resource_type: str,
    partitioner_resource_type: str,
    query: str,
    ui: zf.UI,
):
    """
    **IMPORTANT** this is the sub logic to handle AWS resource like glue table,
    glue job run, that requires the parent resource name in the arguments.

    :param resource_type: for example, ``"glue-table"``
    :param partitioner_resource_type: for example, ``"glue-database"``
    :param query: for example, if the full user query is ``"glue-table: my_database@my table"``,
        then this argument is ``"my_database@my table"``.
    """
    zf.debugger.log(f"search_resource_handler_v2_has_partitioner Query: {query}")
    q = zf.QueryParser(delimiter="@").parse(query)
    # --- search partitioner
    # examples
    # - "  "
    # - "my database"

    # example: " "
    if len(q.trimmed_parts) == 0:
        return search_partitioner_handler(
            resource_type=resource_type,
            partitioner_resource_type=partitioner_resource_type,
            partitioner_query="*",
            ui=ui,
        )
    # example: "my database "
    elif len(q.trimmed_parts) == 1 and len(q.parts) == 1:
        return search_partitioner_handler(
            resource_type=resource_type,
            partitioner_resource_type=partitioner_resource_type,
            partitioner_query=q.trimmed_parts[0],
            ui=ui,
        )
    else:
        pass

    # --- search resource
    # 下面的情况都是需要处理 partitioner 的
    # examples
    # - "my_database@"
    # - "my_database@my table"
    partitioner_query = q.trimmed_parts[0]
    boto_kwargs = _has_partitioner_mapper[resource_type][K_GET_BOTO_KWARGS](
        partitioner_query
    )
    # example: "my_database@  "
    if len(q.trimmed_parts) == 1 and len(q.parts) > 1:
        return search_resource_under_partitioner_handler(
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
        return search_resource_under_partitioner_handler(
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
    :param resource_type: for example, ``"s3-bucket"``
    :param query: for example, if the full user query is ``"s3-bucket: my bucket"``,
        then this argument is ``"my bucket"``.
    """
    if resource_type in _has_partitioner_mapper:
        return search_resource_handler_has_partitioner(
            ui=ui,
            resource_type=resource_type,
            partitioner_resource_type=_has_partitioner_mapper[resource_type][
                K_PARTITIONER_RESOURCE_TYPE
            ],
            query=query,
        )
    else:
        return search_resource_handler_may_has_kwargs(
            ui=ui,
            resource_type=resource_type,
            query=query,
        )


def is_valid_resource_type(resource_type: str) -> bool:
    """
    Check if the given resource_type is a valid value that we support.

    :param resource_type: for example, ec2-instance, s3-bucket
    """
    return resource_type in searchers_metadata


def handler(
    query: str,
    ui: zf.UI,
) -> T.List[T.Union[AwsResourceTypeItem, AwsResourceItem]]:
    """
    Main query handler. It parse the query and route the query to the corresponding
    sub handler.
    """
    # srv id is the service_id-resource_type compound identifier
    # req query is the query string for the resource search
    q = zf.QueryParser(delimiter=":").parse(query)
    # print(f"q.trimmed_parts = {q.trimmed_parts}")

    # example: "  "
    if len(q.trimmed_parts) == 0:
        return select_resource_type_handler(ui=ui, query="*")
    # example:
    # - "ec2 inst"
    # - "s3-bucket"
    # - "ec2 inst: "
    # - "s3-bucket: "
    elif len(q.trimmed_parts) == 1:
        service_query = q.trimmed_parts[0]
        # example:
        # - "ec2 inst: "
        # - "s3-bucket: "
        if len(q.parts) == 1:
            return select_resource_type_handler(ui=ui, query=service_query)
        # example:
        # - "ec2 inst"
        # - "s3-bucket"
        else:
            resource_query = query.split(":")[1].strip()
            # example: "s3-bucket"
            if is_valid_resource_type(service_query):
                return search_resource_handler(
                    resource_type=service_query,
                    query=resource_query,
                    ui=ui,
                )
            # example: "ec2 inst"
            else:
                return select_resource_type_handler(ui=ui, query=service_query)
    # example: "ec2 inst: something", "s3-bucket: something"
    else:
        # example:
        # - s3-bucket: resource query", "s3-bucket" is a valid srv_id
        # use "resource query" to search
        service_query = q.trimmed_parts[0]
        resource_query = query.split(":")[1].strip()
        if is_valid_resource_type(service_query):
            return search_resource_handler(
                resource_type=service_query,
                query=resource_query,
                ui=ui,
            )
        # example: # ec2 inst: something", "ec2 inst" is not a valid srv_id
        else:
            return select_resource_type_handler(ui=ui, query=service_query)


K_PARTITIONER_RESOURCE_TYPE = "partitioner_resource_type"
K_GET_BOTO_KWARGS = "get_boto_kwargs"

# This mapper is used to specify those resource types that require
# a parent resource name for the boto3 API call.
# for example,
# in order to search glue table, you need to specify glue database
# in order to search glue job run, you need to specify glue job
_has_partitioner_mapper = {
    SearcherEnum.glue_table: {
        K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.glue_database,
        K_GET_BOTO_KWARGS: lambda partitioner_query: {
            "DatabaseName": partitioner_query
        },
    },
    SearcherEnum.glue_jobrun: {
        K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.glue_job,
        K_GET_BOTO_KWARGS: lambda partitioner_query: {"JobName": partitioner_query},
    },
    SearcherEnum.sfn_execution: {
        K_PARTITIONER_RESOURCE_TYPE: SearcherEnum.sfn_statemachine,
        K_GET_BOTO_KWARGS: lambda partitioner_query: {
            "stateMachineArn": ars.aws_console.step_function.get_state_machine_arn(
                partitioner_query
            )
        },
    },
}


def run_ui():
    zf.debugger.reset()
    zf.debugger.enable()
    ui = zf.UI(handler=handler, capture_error=False)
    ui.run()

# -*- coding: utf-8 -*-

import typing as T
import subprocess
import dataclasses

import afwf_shell.api as afwf_shell
from boto_session_manager import BotoSesManager

try:
    import pyperclip
except ImportError:
    pass

from .ars import ARS
from .utils import open_url
from .service_searcher import srv_and_res_ds

bsm = BotoSesManager()
ars = ARS(bsm=bsm)


@dataclasses.dataclass
class AwsServiceItem(afwf_shell.Item):
    pass


@dataclasses.dataclass
class AwsResItem(afwf_shell.Item):
    def enter_handler(self, ui: afwf_shell.UI):
        # open AWS console url
        console_url = self.variables["doc"].get("console_url")
        if not console_url:
            console_url = "www.console-url-not-available.com"
        open_url(console_url)

    def ctrl_a_handler(self, ui: afwf_shell.UI):
        # copy ARN
        arn = self.variables["doc"]["raw_data"]["_out"].get("arn", "")
        if arn:
            pyperclip.copy(arn)


def srv_docs_to_srv_items(
    docs: T.Iterable[T.Dict[str, T.Any]],
) -> T.List[AwsServiceItem]:
    return [
        AwsServiceItem(
            uid=doc["id"],
            title=doc["id"],
            subtitle="hit 'Tab' and enter your query to search.",
            arg=doc["id"],
            autocomplete=doc["id"] + ": ",
        )
        for doc in docs
    ]


def res_docs_to_res_items(
    service_id: str,
    resource_type: str,
    docs: T.Iterable[T.Dict[str, T.Any]],
) -> T.List[AwsResItem]:
    items = list()
    for doc in docs:
        autocomplete = doc["raw_data"]["_out"].get("autocomplete")
        if autocomplete:
            autocomplete = f"{service_id}-{resource_type}: {autocomplete}"
        item = AwsResItem(
            uid=doc["id"],
            title=doc["raw_data"]["_out"]["title"],
            subtitle=doc["raw_data"]["_out"].get("subtitle"),
            arg=doc["raw_data"]["_out"].get("arg"),
            autocomplete=autocomplete,
            variables={"doc": doc},
        )
        items.append(item)
    return items


def _list_service() -> T.List[AwsServiceItem]:
    docs = srv_and_res_ds.search(
        download_kwargs={},
        query="*",
        simple_response=True,
        limit=50,
    )
    return srv_docs_to_srv_items(docs)


def _select_service(query: str) -> T.List[AwsServiceItem]:
    """
    :param query: service id and resource type search query input. For example:
        "s3 bucket", "ec2 inst"
    """
    docs = srv_and_res_ds.search(
        download_kwargs={},
        query=query,
        simple_response=True,
        limit=50,
    )
    return srv_docs_to_srv_items(docs)


def print_creating_index(ui: afwf_shell.UI):
    """
    Print a message to tell user that we are creating index.

    This method is used when we need to create or recreate the index.
    """
    items = [
        afwf_shell.Item(
            uid="uid",
            title="Pulling data, it may takes 1-2 minutes ...",
            subtitle="please wait, don't press any key",
        )
    ]
    ui.print_items(items=items)


def sub_handler(
    service_id: str,
    resource_type: str,
    query: str,
    ui: afwf_shell.UI,
) -> T.List[AwsResItem]:
    # print(f"query: {query!r}")
    key = f"{service_id}-{resource_type}"
    service_id, resource_type = key.split("-")
    if key in _special_handler_mapper:
        return _special_handler_mapper[key](query)

    q = afwf_shell.Query.from_str(query)
    final_query = query
    rs = ars._get_rs(service_id, resource_type)

    if len(q.trimmed_parts) == 0:
        final_query = "*"
    if final_query.endswith("!~"):
        print_creating_index(ui)
        final_query = final_query[:-2]
        if not final_query:
            final_query = "*"
        rs.search(q="*", refresh_data=True, limit=1)
        ui.line_editor.press_backspace(n=2)
        ui.move_to_end()
        ui.clear_items()
        ui.clear_query()
        ui.print_query()

    docs = rs.search(
        q=final_query,
        simple_response=True,
        limit=50,
    )
    # rprint(docs[:1])
    return res_docs_to_res_items(
        service_id=service_id,
        resource_type=resource_type,
        docs=docs,
    )


def is_valid_key(ars: ARS, key: str) -> bool:
    """
    :param key: service_id-resource_type compound identifier, for example:
        ec2-instance, s3-bucket
    """
    aws_service_id = key.split("-")[0]
    return bool(ars._data.get(aws_service_id, {}).get(key))


def handler(
    query: str, ui: afwf_shell.UI
) -> T.List[T.Union[AwsServiceItem, AwsResItem]]:
    # srv id is the service_id-resource_type compound identifier
    # req query is the query string for the resource search
    q = afwf_shell.QueryParser(delimiter=":").parse(query)
    # print(f"q.trimmed_parts = {q.trimmed_parts}")

    # example: "  "
    if len(q.trimmed_parts) == 0:
        return _list_service()
    # example: "ec2 inst", "s3-bucket"
    elif len(q.trimmed_parts) == 1:
        # example: "s3-bucket"
        if is_valid_key(ars, q.trimmed_parts[0]):
            service_id, resource_type = q.trimmed_parts[0].split("-")
            return sub_handler(
                service_id=service_id,
                resource_type=resource_type,
                query=query.split(":")[1].strip(),
                ui=ui,
            )
        # example: "ec2 inst"
        else:
            q_res = afwf_shell.Query.from_str(q.trimmed_parts[0])
            return _select_service(query=" ".join(q_res.trimmed_parts))
    # example: "ec2 inst: something", "s3 bucket: something"
    else:
        # example: # s3-bucket: resource query", "s3-bucket" is a valid srv_id
        # use "resource query" to search
        if is_valid_key(ars, q.trimmed_parts[0]):
            service_id, resource_type = q.trimmed_parts[0].split("-")
            return sub_handler(
                service_id=service_id,
                resource_type=resource_type,
                query=query.split(":")[1].strip(),
                ui=ui,
            )
        # example: # ec2 inst: something", "ec2 inst" is not a valid srv_id
        else:
            q_res = afwf_shell.Query.from_str(q.trimmed_parts[0])
            return _select_service(query=" ".join(q_res.trimmed_parts))


# TODO: refactor this ugly code
def search_glue_table(
    query: str,
):
    q = afwf_shell.QueryParser(delimiter=".").parse(query)
    if len(q.trimmed_parts) in [0, 1]:
        if len(q.trimmed_parts) == 0:
            final_query = "*"
        else:
            final_query = q.trimmed_parts[0]
        docs = ars.glue_database.search(
            q=final_query,
            simple_response=True,
            limit=50,
        )
        items = res_docs_to_res_items(
            service_id=ars.glue_table.service_id,
            resource_type=ars.glue_table.resource_type,
            docs=docs,
        )
        for item in items:
            item.title = f"Database: {item.title} (hit tab to search tables)"
            item.autocomplete += "."
        return items
    else:
        q_table = afwf_shell.Query.from_str(q.trimmed_parts[1])
        database = q.trimmed_parts[0]
        if len(q_table.trimmed_parts) == 0:
            final_query = "*"
        else:
            final_query = " ".join(q_table.trimmed_parts[0])
        docs = ars.glue_table.search(
            q=final_query,
            boto_kwargs={"DatabaseName": database},
            simple_response=True,
            limit=50,
        )
        items = res_docs_to_res_items(
            service_id=ars.glue_table.service_id,
            resource_type=ars.glue_table.resource_type,
            docs=docs,
        )
        for item in items:
            database_and_table = item.variables["doc"]["raw_data"]["_out"][
                "database_and_table"
            ]
            item.autocomplete = f"{ars.glue_table.service_id}-{ars.glue_table.resource_type}: {database_and_table}"
        return items


_special_handler_mapper = {
    "glue-table": search_glue_table,
}


def run_ui():
    ui = afwf_shell.UI(handler=handler)
    ui.run()

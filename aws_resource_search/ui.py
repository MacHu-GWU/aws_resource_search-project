# -*- coding: utf-8 -*-

import typing as T
import subprocess
import dataclasses
import afwf_shell.api as afwf_shell
from rich import print as rprint

from boto_session_manager import BotoSesManager

from .ars import ARS
from .service_searcher import srv_and_res_ds

bsm = BotoSesManager()
ars = ARS(bsm=bsm)


@dataclasses.dataclass
class AwsServiceItem(afwf_shell.Item):
    pass


@dataclasses.dataclass
class AwsResItem(afwf_shell.Item):
    def enter_handler(self, ui: afwf_shell.UI):
        subprocess.run(["open", self.variables["doc"]["console_url"]])

    def ctrl_a_handler(self, ui: afwf_shell.UI):
        # copy ARN
        self.variables["doc"]["raw_data"]["_out"].get("arg", "")
        pass


def srv_docs_to_srv_items(
    docs: T.Iterable[T.Dict[str, T.Any]],
) -> T.List[AwsServiceItem]:
    return [
        AwsServiceItem(
            uid=doc["id"],
            title=doc["id"],
            subtitle="no id",
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


def sub_handler(
    service_id: str,
    resource_type: str,
    query: str,
    ui: afwf_shell.UI,
) -> T.List[AwsResItem]:
    print(f"query: {query!r}")
    key = f"{service_id}-{resource_type}"
    service_id, resource_type = key.split("-")
    if key in _mapper:
        return _mapper[key](query)

    q = afwf_shell.Query.from_str(query)
    final_query = query
    rs = ars._get_rs(service_id, resource_type)
    if len(q.trimmed_parts) == 0:
        final_query = "*"
    if final_query.endswith("!~"):
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
    print(f"q.trimmed_parts = {q.trimmed_parts}")

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
    q: str,
):
    parts = q.split(".")
    if len(parts) == 1:
        # print(f"---- q: {q!r}")
        q = parts[0]
        if not q:
            q = "*"
        docs = ars.glue_database.search(
            q=q,
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
        database = parts[0]
        q = parts[1]
        if not q:
            q = "*"
        docs = ars.glue_table.search(
            q=q,
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
    # else:
    #     return [
    #         AwsResItem(
    #             uid="uid",
    #             title="Enter database name to search tables",
    #             subtitle="",
    #             arg="",
    #             variables={},
    #         )
    #     ]


_mapper = {"glue-table": search_glue_table}


def run_ui():
    ui = afwf_shell.UI(handler=handler)
    ui.run()

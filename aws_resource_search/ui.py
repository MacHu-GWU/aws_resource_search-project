# -*- coding: utf-8 -*-

import typing as T
import subprocess
import dataclasses
import afwf_shell.api as afwf_shell
from rich import print as rprint

from boto_session_manager import BotoSesManager

from .ars import ARS
from .service_searcher import srv_and_res_ds

bsm = BotoSesManager(profile_name="edf_sbx_eu_west_1_mfa", region_name="eu-west-1")
ars = ARS(bsm=bsm)


@dataclasses.dataclass
class AwsResItem(afwf_shell.Item):
    def enter_handler(self):
        subprocess.run(["open", self.variables["doc"]["console_url"]])

    def ctrl_a_handler(self):
        # copy ARN
        self.variables["doc"]["raw_data"]["_out"].get("arg", "")
        pass


def docs_to_items(
    service_id: str, resource_type: str, docs: T.Iterable[T.Dict[str, T.Any]]
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


def handler(query: str, ui: afwf_shell.UI):
    # print(f"parts: {query!r}")
    parts = query.split(":", 1)
    if len(parts) == 1:
        q = parts[0]
        if not q:
            q = "*"
        docs = srv_and_res_ds.search(
            download_kwargs={},
            query=q,
            simple_response=True,
            limit=50,
        )
        return [
            afwf_shell.Item(
                uid=doc["id"],
                title=doc["id"],
                subtitle="no id",
                arg=doc["id"],
                autocomplete=doc["id"] + ": ",
            )
            for doc in docs
        ]
    else:
        # print(f"query: {query!r}")
        key = parts[0].strip()
        service_id, resource_type = key.split("-")

        if key in _mapper:
            return _mapper[key](parts[1].strip())

        rs = ars._get_rs(service_id, resource_type)
        q = parts[1].strip()
        if not q:
            q = "*"

        if q.endswith("!~"):
            rs.search(q=q, refresh_data=True)
            ui.line_editor.press_backspace(n=2)
            ui.move_to_end()
            ui.clear_items()
            ui.clear_query()
            ui.print_query()

        # print(f"query: {q!r}")
        docs = rs.search(
            q=q,
            simple_response=True,
            limit=50,
        )
        # rprint(docs[:1])
        return docs_to_items(
            service_id=service_id,
            resource_type=resource_type,
            docs=docs,
        )


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
        items = docs_to_items(
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
        items = docs_to_items(
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

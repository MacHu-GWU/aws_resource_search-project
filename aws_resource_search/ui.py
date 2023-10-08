# -*- coding: utf-8 -*-

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


def handler(query: str):
    # print(f"parts: {query!r}")
    parts = query.split(":", 1)
    if len(parts) == 1:
        q = parts[0]
        if not q:
            q = "*"
        docs = srv_and_res_ds.search(download_kwargs={}, query=q, simple_response=True)
        # print(docs[0])
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
        service_id, resource_type = parts[0].strip().split("-")
        # print([service_id, resource_type])
        rs = ars._get_rs(service_id, resource_type)
        q = parts[1].strip()
        if not q:
            q = "*"
        # print(f"query: {q!r}")
        docs =  rs.search(
            q=q,
            simple_response=True,
        )
        # rprint(docs[:1])
        return [
            AwsResItem(
                uid=doc["id"],
                title=doc["raw_data"]["_out"]["title"],
                subtitle=doc["raw_data"]["_out"]["subtitle"],
                arg=doc["id"],
                variables={"doc": doc},
            )
            for doc in docs
        ]


def run_ui():
    ui = afwf_shell.UI(handler=handler)
    ui.run()

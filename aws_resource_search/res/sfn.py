# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

from .. import res_lib

if T.TYPE_CHECKING:
    from ..ars_v2 import ARS


@dataclasses.dataclass
class SfnStateMachine(res_lib.BaseDocument):
    type: str = dataclasses.field()
    create_at: datetime = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    sm_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            type=resource["type"],
            create_at=resource["creationDate"],
            id=resource["name"],
            name=resource["name"],
            sm_arn=resource["stateMachineArn"],
        )

    @property
    def title(self) -> str:
        return self.name

    @property
    def subtitle(self) -> str:
        return f"<type>: {self.type}, <create_at>: {str(self.create_at)[:19]}"

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.sm_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.step_function.get_state_machine_view_tab(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        res = ars.bsm.sfn_client.describe_state_machine(stateMachineArn=self.arn)
        status = res["status"]
        role_arn = res["roleArn"]
        definition = res["definition"]
        type = res["type"]
        creation_date = res["creationDate"]

        res = ars.bsm.sfn_client.list_tags_for_resource(resourceArn=self.arn)
        tags: dict = {dct["key"]: dct["value"] for dct in res.get("tags", [])}
        tag_items = res_lib.DetailItem.from_tags(tags)

        return [
            res_lib.DetailItem(
                title=f"<status>: {status}",
                subtitle="📋 Tap 'Ctrl + A' to copy.",
                uid="status",
                variables={
                    "copy": status,
                    "url": None,
                },
            ),
            res_lib.DetailItem(
                title=f"🧢 <role_arn>: {role_arn}",
                subtitle="🌐 Tap 'Enter' to open url, 📋 tap 'Ctrl + A' to copy",
                uid="role_arn",
                variables={
                    "copy": role_arn,
                    "url": ars.aws_console.iam.get_role(name_or_arn=role_arn),
                },
            ),
            res_lib.DetailItem(
                title=f"<definition>: {definition}",
                subtitle="📋 Tap 'Ctrl + A' to copy.",
                uid="definition",
                variables={
                    "copy": definition,
                    "url": None,
                },
            ),
            res_lib.DetailItem(
                title=f"<type>: {type}",
                subtitle="📋 Tap 'Ctrl + A' to copy.",
                uid="type",
                variables={
                    "copy": type,
                    "url": None,
                },
            ),
            res_lib.DetailItem(
                title=f"<creation_date>: {creation_date}",
                subtitle="📋 Tap 'Ctrl + A' to copy.",
                uid="creation_date",
                variables={
                    "copy": str(creation_date),
                    "url": None,
                },
            ),
            *tag_items,
        ]


sfn_state_machine_searcher = res_lib.Searcher(
    # list resources
    service="stepfunctions",
    method="list_state_machines",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("stateMachines"),
    # extract document
    doc_class=SfnStateMachine,
    # search
    resource_type="sfn-statemachine",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="type"),
        res_lib.sayt.StoredField(name="create_at"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="sm_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


_sfn_execution_status_mapper = {
    "RUNNING": "🔵",
    "SUCCEEDED": "🟢",
    "FAILED": "🔴",
    "TIMED_OUT": "🔴",
    "ABORTED'": "⚫",
}


@dataclasses.dataclass
class SfnExecution(res_lib.BaseDocument):
    sm_name: str = dataclasses.field()
    start_at: datetime = dataclasses.field()
    end_at: datetime = dataclasses.field()
    status: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    exec_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            sm_name=resource["stateMachineArn"].split(":")[-1],
            start_at=resource.get("startDate"),
            end_at=resource.get("stopDate"),
            status=resource["status"],
            id=resource["executionArn"].split(":")[-1],
            name=resource["executionArn"].split(":")[-1],
            exec_arn=resource["executionArn"],
        )

    @property
    def title(self) -> str:
        return f"{self.name}, <state>: {_sfn_execution_status_mapper[self.status]} {self.status}"

    @property
    def subtitle(self) -> str:
        return (
            f"<sm>: {self.sm_name}, "
            f"<start>: {str(self.start_at)[:19]}, "
            f"<end>: {str(self.end_at)[:19]}"
        )

    @property
    def autocomplete(self) -> str:
        return f"{self.sm_name}@{self.name}"

    @property
    def arn(self) -> str:
        return self.exec_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.step_function.get_state_machine_execution(
            exec_id_or_arn=self.arn
        )


sfn_execution_searcher = res_lib.Searcher(
    # list resources
    service="stepfunctions",
    method="list_executions",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("executions"),
    # extract document
    doc_class=SfnExecution,
    # search
    resource_type="sfn-execution",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="sm_name"),
        res_lib.sayt.StoredField(name="start_at"),
        res_lib.sayt.StoredField(name="end_at"),
        res_lib.sayt.StoredField(name="status"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="exec_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

from .. import res_lib
from ..terminal import format_key_value, highlight_text

if T.TYPE_CHECKING:
    from ..ars_v2 import ARS


sfn_statemachine_status_icon_mapper = {
    "ACTIVE": "🟢",
    "DELETING": "🔴",
}


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
        return "{}, {}, {}".format(
            format_key_value("type", self.type),
            format_key_value("create_at", self.create_at),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.sm_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.step_function.get_state_machine_view_tab(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        # fmt: off
        res = ars.bsm.sfn_client.describe_state_machine(stateMachineArn=self.arn)
        state_machine_arn = res["stateMachineArn"]
        status = res["status"]
        role_arn = res["roleArn"]
        definition = res["definition"]
        type = res["type"]
        creation_date = res["creationDate"]

        status_icon = sfn_statemachine_status_icon_mapper[status]
        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        detail_items = [
            Item("state_machine_arn", state_machine_arn, url=aws.step_function.get_state_machine_view_tab(state_machine_arn)),
            Item("status", status, text=f"{status_icon} {status}"),
            Item("🧢 role_arn", role_arn, url=aws.iam.get_role(role_arn)),
            Item("definition", definition),
            Item("type", type),
            Item("creation_date", creation_date),
        ]

        res = ars.bsm.sfn_client.list_tags_for_resource(resourceArn=self.arn)
        tags: dict = {dct["key"]: dct["value"] for dct in res.get("tags", [])}
        tag_items = res_lib.DetailItem.from_tags(tags)
        # fmt: on

        return [
            *detail_items,
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


sfn_execution_status_icon_mapper = {
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
        return "{}, {}".format(
            highlight_text(self.name),
            format_key_value("status", f"{sfn_execution_status_icon_mapper[self.status]} {self.status}")
        )

    @property
    def subtitle(self) -> str:
        return (
            "{}, {}".format(
                format_key_value("start", self.start_at),
                format_key_value("end", self.end_at),
            )
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

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        # fmt: off
        res = ars.bsm.sfn_client.describe_execution(executionArn=self.arn)
        exec_arn = res["executionArn"]
        status = res["status"]
        state_machine_arn = res["stateMachineArn"]
        state_machine_version_arn = res.get("stateMachineVersionArn")
        state_machine_alias_arn = res.get("stateMachineAliasArn")
        input = res["input"]
        output = res["output"]
        error = res.get("error")
        cause = res.get("cause")

        status_icon = sfn_execution_status_icon_mapper[status]
        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        detail_items = [
            Item("exec_arn", exec_arn, url=aws.step_function.get_state_machine_execution(exec_arn)),
            Item("status", status, text=f"{status_icon} {status}"),
            Item("state_machine_arn", state_machine_arn, url=aws.step_function.get_state_machine_view_tab(state_machine_arn)),
            Item("state_machine_version_arn", state_machine_version_arn) if state_machine_version_arn else None,
            Item("state_machine_alias_arn", state_machine_alias_arn) if state_machine_alias_arn else None,
            Item("input", input),
            Item("output", output) if output else None,
            Item("error", error) if error else None,
            Item("cause", cause) if cause else None,
        ]
        detail_items = [item for item in detail_items if item is not None]
        # fmt: on

        return [
            *detail_items,
        ]


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

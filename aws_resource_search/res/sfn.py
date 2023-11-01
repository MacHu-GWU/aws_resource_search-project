# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses
from datetime import datetime

from .. import res_lib
from ..terminal import format_key_value

if T.TYPE_CHECKING:
    from ..ars import ARS


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
            type=resource.get("type", "Unknown"),
            create_at=resource["creationDate"],
            id=resource["name"],
            name=resource["name"],
            sm_arn=resource["stateMachineArn"],
        )

    @property
    def title(self) -> str:
        return format_key_value("name", self.name)

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

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars, arn_field_name="statemachine_arn")

        with self.enrich_details(detail_items):
            res = ars.bsm.sfn_client.describe_state_machine(stateMachineArn=self.arn)
            status = res["status"]
            role_arn = res["roleArn"]
            definition = res["definition"]
            type = res.get("type", "Unknown")
            creation_date = res["creationDate"]

            status_icon = sfn_statemachine_status_icon_mapper[status]
            detail_items.extend([
                Item("status", status, text=f"{status_icon} {status}"),
                Item("🧢 role_arn", role_arn, url=ars.aws_console.iam.get_role(role_arn)),
                Item("definition", json.dumps(json.loads(definition))),
                Item("type", type),
                Item("creation_date", creation_date),
            ])

        with self.enrich_details(detail_items):
            res = ars.bsm.sfn_client.list_tags_for_resource(resourceArn=self.arn)
            tags: dict = {dct["key"]: dct["value"] for dct in res.get("tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items
    # fmt: on


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
            start_at=resource.get("startDate", "NA"),
            end_at=resource.get("stopDate", "NA"),
            status=resource["status"],
            id=resource["executionArn"].split(":")[-1],
            name=resource["executionArn"].split(":")[-1],
            exec_arn=resource["executionArn"],
        )

    @property
    def title(self) -> str:
        return format_key_value("execution_name", self.name)

    @property
    def subtitle(self) -> str:
        status_icon = sfn_execution_status_icon_mapper[self.status]
        return "{}, {}, {}, {}".format(
            f"{status_icon} {self.status}",
            format_key_value("start", self.start_at),
            format_key_value("end", self.end_at),
            self.short_subtitle,
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

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars, arn_field_name="exec_arn")

        with self.enrich_details(detail_items):
            res = ars.bsm.sfn_client.describe_execution(executionArn=self.arn)
            status = res["status"]
            state_machine_arn = res["stateMachineArn"]
            state_machine_version_arn = res.get("stateMachineVersionArn")
            state_machine_alias_arn = res.get("stateMachineAliasArn")
            input = res["input"]
            output = res.get("output")
            error = res.get("error")
            cause = res.get("cause")

            status_icon = sfn_execution_status_icon_mapper[status]
            detail_items.extend([
                Item("status", status, text=f"{status_icon} {status}"),
                Item("state_machine_arn", state_machine_arn, url=ars.aws_console.step_function.get_state_machine_view_tab(state_machine_arn)),
                Item("state_machine_version_arn", state_machine_version_arn) if state_machine_version_arn else None,
                Item("state_machine_alias_arn", state_machine_alias_arn) if state_machine_alias_arn else None,
                Item("input", self.one_line(input)),
                Item("output", self.one_line(output)),
                Item("error", self.one_line(error)),
                Item("cause", self.one_line(cause)),
            ])

        detail_items = [item for item in detail_items if item is not None]
        return detail_items
    # fmt: on

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
    more_cache_key=lambda boto_kwargs: [boto_kwargs["stateMachineArn"]],
)


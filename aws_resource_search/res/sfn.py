# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

import aws_console_url.api as acu
import sayt.api as sayt

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


sfn_statemachine_status_icon_mapper = {
    "ACTIVE": "🟢",
    "DELETING": "🔴",
}

sfn_statemachine_type_icon_mapper = {
    "STANDARD": "⌛",
    "EXPRESS": "🚀",
}


@dataclasses.dataclass
class SfnStateMachine(rl.ResourceDocument):
    # fmt: off
    type: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="type", minsize=2, maxsize=4, stored=True)})
    # fmt: on

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["name"],
            name=resource["name"],
            type=resource.get("type", "STANDARD"),
        )

    @property
    def state_machine_name(self) -> str:
        return self.name

    @property
    def title(self) -> str:
        return rl.format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        type_icon = sfn_statemachine_type_icon_mapper[self.type]
        return "{}, {}".format(
            rl.format_key_value("type", f"{type_icon} {self.type}"),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data["stateMachineArn"]

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.step_function.get_state_machine_view_tab(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.step_function.state_machines

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars, arn_key="statemachine_arn")

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.sfn_client.describe_state_machine(stateMachineArn=self.arn)
            status = res["status"]
            role_arn = res["roleArn"]
            definition = res["definition"]
            type = res.get("type", "STANDARD")
            creation_date = res["creationDate"]

            status_icon = sfn_statemachine_status_icon_mapper[status]
            type_icon = sfn_statemachine_type_icon_mapper[type]
            detail_items.extend([
                from_detail("status", status, value_text=f"{status_icon} {status}", url=url),
                from_detail("🧢 role_arn", role_arn, url=ars.aws_console.iam.get_role(role_arn)),
                from_detail("definition", definition, value_text=self.one_line(definition), url=url),
                from_detail("type", type, value_text=f"{type_icon} {type}", url=url),
                from_detail("creation_date", creation_date, url=url),
            ])

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.sfn_client.list_tags_for_resource(resourceArn=self.arn)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class SfnStateMachineSearcher(rl.BaseSearcher[SfnStateMachine]):
    pass


sfn_state_machine_searcher = SfnStateMachineSearcher(
    # list resources
    service="stepfunctions",
    method="list_state_machines",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("stateMachines"),
    # extract document
    doc_class=SfnStateMachine,
    # search
    resource_type=rl.SearcherEnum.sfn_state_machine.value,
    fields=SfnStateMachine.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.sfn_state_machine.value),
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
class SfnExecution(rl.ResourceDocument):
    # fmt: off
    status: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="status", minsize=2, maxsize=4, stored=True)})
    start_at: datetime = dataclasses.field(metadata={"field": sayt.DatetimeField(name="start_at", sortable=True, ascending=False, stored=True)})
    # fmt: on

    @property
    def state_machine_name(self) -> str:
        return self.raw_data["stateMachineArn"].split(":")[-1]

    @property
    def end_at(self) -> datetime:
        return rl.get_datetime(self.raw_data, "stopDate")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["executionArn"].split(":")[-1],
            name=resource["executionArn"].split(":")[-1],
            status=resource["status"],
            start_at=rl.get_datetime(resource, "startDate"),
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("execution_name", self.name)

    @property
    def subtitle(self) -> str:
        status_icon = sfn_execution_status_icon_mapper[self.status]
        return "{}, {}, {}, {}".format(
            f"{status_icon} {self.status}",
            rl.format_key_value("start", self.start_at),
            rl.format_key_value("end", self.end_at),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return f"{self.state_machine_name}@{self.name}"

    @property
    def arn(self) -> str:
        return self.raw_data["executionArn"]

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.step_function.get_state_machine_execution(
            exec_id_or_arn=self.arn
        )

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars, arn_key="exec_arn")

        with rl.DetailItem.error_handling(detail_items):
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
                from_detail("status", status, value_text=f"{status_icon} {status}", url=url),
                from_detail("state_machine_arn", state_machine_arn, url=ars.aws_console.step_function.get_state_machine_view_tab(state_machine_arn)),
                from_detail("state_machine_version_arn", state_machine_version_arn, url=url) if state_machine_version_arn else None,
                from_detail("state_machine_alias_arn", state_machine_alias_arn, url=url) if state_machine_alias_arn else None,
                from_detail("input", input, value_text=self.one_line(input), url=url),
                from_detail("output", output, value_text=self.one_line(output), url=url),
                from_detail("error", error, value_text=self.one_line(error), url=url),
                from_detail("cause", cause, value_text=self.one_line(cause), url=url),
            ])

        detail_items = [item for item in detail_items if item is not None]
        return detail_items
    # fmt: on


class SfnExecutionSearcher(rl.BaseSearcher[SfnExecution]):
    pass


sfn_execution_searcher = SfnExecutionSearcher(
    # list resources
    service="stepfunctions",
    method="list_executions",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("executions"),
    # extract document
    doc_class=SfnExecution,
    # search
    resource_type=rl.SearcherEnum.sfn_state_machine_execution.value,
    fields=SfnExecution.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(
        rl.SearcherEnum.sfn_state_machine_execution.value
    ),
    more_cache_key=lambda boto_kwargs: [boto_kwargs["stateMachineArn"]],
)

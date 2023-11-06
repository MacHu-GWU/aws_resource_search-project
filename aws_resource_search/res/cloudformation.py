# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

from .. import res_lib
from ..terminal import format_key_value, ShortcutEnum
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


cloudformation_stack_status_icon_mapper = {
    "CREATE_IN_PROGRESS": "🟡",
    "CREATE_FAILED": "🔴",
    "CREATE_COMPLETE": "🟢🟢",
    "ROLLBACK_IN_PROGRESS": "🟡",
    "ROLLBACK_FAILED": "🔴",
    "ROLLBACK_COMPLETE": "🟢🟡",
    "DELETE_IN_PROGRESS": "🟡",
    "DELETE_FAILED": "🔴",
    "DELETE_COMPLETE": "🟢🔴",
    "UPDATE_IN_PROGRESS": "🟡",
    "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS": "🟡",
    "UPDATE_COMPLETE": "🟢🟢",
    "UPDATE_FAILED": "🔴",
    "UPDATE_ROLLBACK_IN_PROGRESS": "🟡",
    "UPDATE_ROLLBACK_FAILED": "🔴",
    "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS": "🟡",
    "UPDATE_ROLLBACK_COMPLETE": "🟢🟡",
    "REVIEW_IN_PROGRESS": "🟡",
    "IMPORT_IN_PROGRESS": "🟡",
    "IMPORT_COMPLETE": "🟢🟢",
    "IMPORT_ROLLBACK_IN_PROGRESS": "🟡",
    "IMPORT_ROLLBACK_FAILED": "🔴",
    "IMPORT_ROLLBACK_COMPLETE'": "🟢🟡",
}


@dataclasses.dataclass
class CloudFormationStack(res_lib.BaseDocument):
    status: str = dataclasses.field()
    last_updated_time: datetime = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["StackName"],
            name=resource["StackName"],
            status=resource["StackStatus"],
            last_updated_time=res_lib.get_datetime(resource, "LastUpdatedTime"),
        )

    @property
    def title(self) -> str:
        return format_key_value("stack_name", self.name)

    @property
    def subtitle(self) -> str:
        status_icon = cloudformation_stack_status_icon_mapper[self.status]
        return "{}, {}, {}".format(
            f"{status_icon} {self.status}",
            format_key_value(
                "update_at", res_lib.to_simple_fmt(self.last_updated_time)
            ),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data["StackId"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.cloudformation.get_stack(name_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = [] # don't use self.get_initial_detail_items here, the arn may not change

        with self.enrich_details(detail_items):
            res = ars.bsm.cloudformation_client.describe_stacks(StackName=self.name)
            stacks = res.get("Stacks", [])
            if len(stacks) == 0:
                return [
                    res_lib.DetailItem.new(
                        title="🚨 Stack not found, maybe it's deleted?",
                        subtitle=f"{ShortcutEnum.ENTER} to verify in AWS Console",
                        url=ars.aws_console.cloudformation.filter_stack(name=self.name),
                    )
                ]
            stack = stacks[0]
            arn = stack["StackId"]
            url = ars.aws_console.cloudformation.get_stack(arn)

            status = stack["StackStatus"]
            role_arn = stack.get("RoleARN", "NA")
            status_icon = cloudformation_stack_status_icon_mapper[self.status]
            detail_items = [
                from_detail("arn", arn, url=url),
                from_detail("status", status, text=f"{status_icon} {status}", url=url),
                from_detail("role_arn", role_arn, url=ars.aws_console.iam.get_role(role_arn)),
            ]

            outputs: dict = {dct["OutputKey"]: dct for dct in stack.get("Outputs", [])}
            detail_items.extend(
                [
                    res_lib.DetailItem.new(
                        title="🎯 output: {} (export = {})".format(
                            format_key_value(k, dct["OutputValue"]),
                            dct.get("ExportName", "NA"),
                        ),
                        subtitle=f"🌐 {ShortcutEnum.ENTER} to open url, 📋 {ShortcutEnum.CTRL_A} to copy value.",
                        copy=dct["OutputValue"],
                        url=url,
                        uid=f"Output {k}",
                    )
                    for k, dct in outputs.items()
                ]
            )

            tags: dict = {dct["Key"]: dct["Value"] for dct in stack.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))
        return detail_items
    # fmt: on


class CloudFormationStackSearcher(res_lib.Searcher[CloudFormationStack]):
    pass


cloudformation_stack_searcher = CloudFormationStackSearcher(
    # list resources
    service="cloudformation",
    method="list_stacks",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {
            "MaxItems": 9999,
        },
    },
    result_path=res_lib.ResultPath("StackSummaries"),
    # extract document
    doc_class=CloudFormationStack,
    # search
    resource_type=SearcherEnum.cloudformation_stack,
    fields=res_lib.define_fields(
        fields=[
            res_lib.sayt.NgramWordsField(
                name="status",
                minsize=2,
                maxsize=4,
                stored=True,
            ),
            res_lib.sayt.DatetimeField(
                name="last_updated_time",
                sortable=True,
                ascending=False,
                stored=True,
            ),
        ],
        name_sortable=False,
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

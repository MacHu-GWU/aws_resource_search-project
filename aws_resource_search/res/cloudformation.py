# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from .. import res_lib
from ..terminal import format_key_value, ShortcutEnum
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


cloudformation_stack_status_icon_mapper = {
    "CREATE_IN_PROGRESS": "🟡",
    "CREATE_FAILED": "🔴",
    "CREATE_COMPLETE": "🟢",
    "ROLLBACK_IN_PROGRESS": "🟡",
    "ROLLBACK_FAILED": "🔴",
    "ROLLBACK_COMPLETE": "🟢",
    "DELETE_IN_PROGRESS": "🟡",
    "DELETE_FAILED": "🔴",
    "DELETE_COMPLETE": "🟢",
    "UPDATE_IN_PROGRESS": "🟡",
    "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS": "🟡",
    "UPDATE_COMPLETE": "🟢",
    "UPDATE_FAILED": "🔴",
    "UPDATE_ROLLBACK_IN_PROGRESS": "🟡",
    "UPDATE_ROLLBACK_FAILED": "🔴",
    "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS": "🟡",
    "UPDATE_ROLLBACK_COMPLETE": "🟢",
    "REVIEW_IN_PROGRESS": "🟡",
    "IMPORT_IN_PROGRESS": "🟡",
    "IMPORT_COMPLETE": "🟢",
    "IMPORT_ROLLBACK_IN_PROGRESS": "🟡",
    "IMPORT_ROLLBACK_FAILED": "🔴",
    "IMPORT_ROLLBACK_COMPLETE'": "🟢",
}


@dataclasses.dataclass
class CloudFormationStack(res_lib.BaseDocument):
    status: str = dataclasses.field()
    role_arn: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    stack_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            status=resource["StackStatus"],
            role_arn=resource.get("RoleARN", "NA"),
            id=resource["StackName"],
            name=resource["StackName"],
            stack_arn=resource["StackId"],
        )

    @property
    def title(self) -> str:
        return format_key_value("stack_name", self.name)

    @property
    def subtitle(self) -> str:
        status_icon = cloudformation_stack_status_icon_mapper[self.status]
        return "{}, {}".format(
            f"{status_icon} {self.status}",
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.stack_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.cloudformation.get_stack(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console

        detail_items = []
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
            status = stack["StackStatus"]
            role_arn = stack.get("RoleARN", "NA")
            status_icon = cloudformation_stack_status_icon_mapper[self.status]
            detail_items = [
                Item("arn", arn, url=aws.cloudformation.get_stack(arn)),
                Item("status", status, text=f"{status_icon} {status}"),
                Item("role_arn", role_arn, url=aws.iam.get_role(role_arn)),
            ]

            outputs: dict = {dct["OutputKey"]: dct for dct in stack.get("Outputs", [])}
            detail_items.extend(
                [
                    res_lib.DetailItem(
                        title="🎯 output: {} (export = {})".format(
                            format_key_value(k, dct["OutputValue"]),
                            dct.get("ExportName", "NA"),
                        ),
                        subtitle=f"📋 {ShortcutEnum.CTRL_A} to copy the value.",
                        uid=f"Output {k}",
                        variables={"copy": dct["OutputValue"], "url": None},
                    )
                    for k, dct in outputs.items()
                ]
            )

            tags: dict = {dct["Key"]: dct["Value"] for dct in stack.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))
        return detail_items


class CloudFormationStackSearcher(res_lib.Searcher[CloudFormationStack]):
    pass


cloudformation_stack_searcher = CloudFormationStackSearcher(
    # list resources
    service="cloudformation",
    method="describe_stacks",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {
            "MaxItems": 9999,
        },
    },
    result_path=res_lib.ResultPath("Stacks"),
    # extract document
    doc_class=CloudFormationStack,
    # search
    resource_type=SearcherEnum.cloudformation_stack,
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.NgramWordsField(name="status", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="role_arn"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="stack_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

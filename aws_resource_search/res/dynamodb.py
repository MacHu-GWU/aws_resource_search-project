# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import ShortcutEnum, format_key_value
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS

dynamodb_table_status_icon_mapper = {
    "CREATING": "🟡",
    "UPDATING": "🟡",
    "DELETING": "🔴",
    "ACTIVE": "🟢",
    "INACCESSIBLE_ENCRYPTION_CREDENTIALS": "🔴",
    "ARCHIVING": "🟡",
    "ARCHIVED": "🔴",
}


@dataclasses.dataclass
class DynamodbTable(res_lib.BaseDocument):
    table_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource,
            name=resource,
            table_arn=arns.res.DynamodbTable.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                table_name=resource,
            ).to_arn(),
        )

    @property
    def title(self) -> str:
        return format_key_value("table_name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.table_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.dynamodb.get_table(table_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.dynamodb_client.describe_table(TableName=self.name)
            dct = res["Table"]

            attrs = {d["AttributeName"]: d["AttributeType"] for d in dct.get("AttributeDefinitions", [])}
            keys = {d["AttributeName"]: d["KeyType"] for d in dct.get("KeySchema", [])}
            for attr_name, key_type in keys.items():
                data_type = attrs[attr_name]
                item = res_lib.DetailItem.new(
                    title="🔑 key_schema {}, {}, {}".format(
                        format_key_value("key", attr_name),
                        format_key_value("key_type", key_type),
                        format_key_value("data_type", data_type),
                    ),
                    subtitle=f"🌐 {ShortcutEnum.ENTER} to open url, 📋 {ShortcutEnum.CTRL_A} to copy key name.",
                )
                detail_items.append(item)

            TableSizeBytes = dct.get("TableSizeBytes", "Unknown")
            ItemCount = dct.get("ItemCount", "Unknown")
            BillingMode = dct.get("BillingModeSummary", {}).get("BillingMode", "Unknown")
            TableClass = dct.get("TableClassSummary", {}).get("BillingMode", "Unknown")
            detail_items.extend(
                [
                    from_detail("TableSizeBytes", TableSizeBytes, url=url),
                    from_detail("ItemCount", ItemCount, url=url),
                    from_detail("BillingMode", BillingMode, url=url),
                    from_detail("TableClass", TableClass, url=url),
                ]
            )

        with self.enrich_details(detail_items):
            res = ars.bsm.dynamodb_client.list_tags_of_resource(ResourceArn=self.arn)
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class DynamodbTableSearcher(res_lib.Searcher[DynamodbTable]):
    pass


dynamodb_table_searcher = DynamodbTableSearcher(
    # list resources
    service="dynamodb",
    method="list_tables",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {"MaxItems": 9999, "PageSize": 100},
    },
    result_path=res_lib.ResultPath("TableNames"),
    # extract document
    doc_class=DynamodbTable,
    # search
    resource_type=SearcherEnum.dynamodb_table,
    fields=res_lib.define_fields(
        fields=[
            res_lib.sayt.StoredField(name="table_arn"),
        ],
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

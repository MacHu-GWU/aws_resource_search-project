# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import sayt.api as sayt
import aws_arns.api as arns
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS

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
class DynamodbTable(rl.ResourceDocument):
    # fmt: off
    table_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="table_arn")})
    # fmt: on

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
        return rl.format_key_value("table_name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.table_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.dynamodb.get_table(table_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.dynamodb.tables

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.dynamodb_client.describe_table(TableName=self.name)
            dct = res["Table"]

            attrs = {d["AttributeName"]: d["AttributeType"] for d in dct.get("AttributeDefinitions", [])}
            keys = {d["AttributeName"]: d["KeyType"] for d in dct.get("KeySchema", [])}
            for attr_name, key_type in keys.items():
                data_type = attrs[attr_name]
                item = rl.DetailItem.new(
                    title="🔑 key_schema {}, {}, {}".format(
                        rl.format_key_value("key", attr_name),
                        rl.format_key_value("key_type", key_type),
                        rl.format_key_value("data_type", data_type),
                    ),
                    subtitle=f"🌐 {rl.ShortcutEnum.ENTER} to open url, 📋 {rl.ShortcutEnum.CTRL_A} to copy key name.",
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

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.dynamodb_client.list_tags_of_resource(ResourceArn=self.arn)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url=url))

        return detail_items
    # fmt: on


class DynamodbTableSearcher(rl.BaseSearcher[DynamodbTable]):
    pass


dynamodb_table_searcher = DynamodbTableSearcher(
    # list resources
    service="dynamodb",
    method="list_tables",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {"MaxItems": 9999, "PageSize": 100},
    },
    result_path=rl.ResultPath("TableNames"),
    # extract document
    doc_class=DynamodbTable,
    # search
    resource_type=rl.SearcherEnum.dynamodb_table.value,
    fields=DynamodbTable.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.dynamodb_table.value),
    more_cache_key=None,
)

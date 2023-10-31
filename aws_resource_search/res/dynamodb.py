# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value

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
    id: str = dataclasses.field()
    name: str = dataclasses.field()
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

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)

        with self.enrich_details(detail_items):
            res = ars.bsm.dynamodb_client.describe_table(TableName=self.name)
            dct = res["Table"]
            TableSizeBytes = dct.get("TableSizeBytes", "Unknown")
            ItemCount = dct.get("ItemCount", "Unknown")
            BillingMode = dct.get("BillingModeSummary", {}).get(
                "BillingMode", "Unknown"
            )
            TableClass = dct.get("TableClassSummary", {}).get("BillingMode", "Unknown")
            detail_items.extend(
                [
                    Item("TableSizeBytes", TableSizeBytes),
                    Item("ItemCount", ItemCount),
                    Item("BillingMode", BillingMode),
                    Item("TableClass", TableClass),
                ]
            )

        with self.enrich_details(detail_items):
            res = ars.bsm.dynamodb_client.list_tags_of_resource(ResourceArn=self.arn)
            tags: dict = {dct["key"]: dct["value"] for dct in res.get("tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items


dynamodb_table_searcher = res_lib.Searcher(
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
    resource_type="dynamodb-table",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="table_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

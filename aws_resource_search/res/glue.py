# -*- coding: utf-8 -*-

import dataclasses
from .. import res_lib


@dataclasses.dataclass
class GlueTable(res_lib.BaseDocument):
    catalog_id: str = dataclasses.field()
    database: str = dataclasses.field()
    table: str = dataclasses.field()
    description: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    table_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            catalog_id=resource["CatalogId"],
            database=resource["DatabaseName"],
            table=resource["Name"],
            description=resource.get("Description", "No Description"),
            id="{}.{}".format(resource["DatabaseName"], resource["Name"]),
            name="{}.{}".format(resource["DatabaseName"], resource["Name"]),
            table_arn="arn:aws:glue:{aws_region}:{aws_account_id}:table/{database}/{table}".format(
                aws_region=bsm.aws_region,
                aws_account_id=bsm.aws_account_id,
                database=resource["DatabaseName"],
                table=resource["Name"],
            ),
        )

    @property
    def database_and_table(self) -> str:
        return f"{self.database}.{self.table}"

    @property
    def title(self) -> str:
        return self.database_and_table

    @property
    def subtitle(self) -> str:
        return self.description

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.table_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.glue.get_table(table_or_arn=self.arn)


glue_table_searcher = res_lib.Searcher(
    # list resources
    service="glue",
    method="get_tables",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("TableList"),
    # extract document
    doc_class=GlueTable,
    # search
    resource_type="glue-table",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="catalog_id"),
        res_lib.sayt.StoredField(name="database"),
        res_lib.sayt.StoredField(name="table"),
        res_lib.sayt.StoredField(name="description"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="table_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class SsmParameter(res_lib.BaseDocument):
    type: str = dataclasses.field()
    last_modified_date: datetime = dataclasses.field()
    description: str = dataclasses.field()
    tier: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    param_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            type=resource["Type"],
            last_modified_date=resource["LastModifiedDate"],
            description=resource.get("Description", "No description"),
            tier=resource["Tier"],
            id=resource["Name"],
            name=resource["Name"],
            param_arn=arns.res.SSMParameter.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                name=resource["Name"],
            ).to_arn(),
        )

    @property
    def title(self) -> str:
        return format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            format_key_value("type", self.type),
            format_key_value("tier", self.tier),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.param_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.ssm.get_parameter(name_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)

        with self.enrich_details(detail_items):
            detail_items.extend([
                Item("Type", self.raw_data.get("Type", "NA")),
                Item("KeyId", self.raw_data.get("KeyId", "NA")),
                Item("LastModifiedDate", self.raw_data.get("LastModifiedDate", "NA")),
                Item("LastModifiedUser", self.raw_data.get("LastModifiedUser", "NA")),
                Item("Description", self.raw_data.get("Description", "NA")),
                Item("AllowedPattern", self.raw_data.get("AllowedPattern", "NA")),
                Item("Version", self.raw_data.get("Version", "NA")),
                Item("Tier", self.raw_data.get("Tier", "NA")),
                Item("DataType", self.raw_data.get("DataType", "NA")),
            ])

        with self.enrich_details(detail_items):
            res = ars.bsm.ssm_client.list_tags_for_resource(
                ResourceType="Parameter",
                ResourceId=self.name,
            )
            tags: dict = {dct["key"]: dct["value"] for dct in res.get("TagList", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items
    # fmt: on


ssm_parameter_searcher = res_lib.Searcher(
    # list resources
    service="ssm",
    method="describe_parameters",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 50}},
    result_path=res_lib.ResultPath("Parameters"),
    # extract document
    doc_class=SsmParameter,
    # search
    resource_type="ssm-parameter",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.NgramWordsField(name="type", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="description"),
        res_lib.sayt.StoredField(name="last_modified_date"),
        res_lib.sayt.NgramWordsField(name="tier", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="param_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

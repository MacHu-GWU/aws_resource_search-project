# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class SsmParameter(res_lib.BaseDocument):
    type: str = dataclasses.field()
    tier: str = dataclasses.field()
    param_arn: str = dataclasses.field()

    @property
    def last_modified_date(self) -> datetime:
        return res_lib.get_datetime(self.raw_data, "LastModifiedDate")

    @property
    def description(self) -> str:
        return res_lib.get_description(self.raw_data, "Description")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            type=resource["Type"],
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
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.ssm_client.get_parameter(Name=self.name)
            param = res["Parameter"]
            detail_items.extend([
                from_detail("LastModifiedDate", self.raw_data.get("LastModifiedDate", "NA"), url=url),
                from_detail("Type", param.get("Type", "NA"), url=url),
                from_detail("Version", param.get("Version", "NA"), url=url),
                from_detail("DataType", param.get("DataType", "NA"), url=url),
                from_detail("Value", param.get("Value", "NA"), self.one_line(param.get("Value", "NA")), url=url),
            ])

        with self.enrich_details(detail_items):
            res = ars.bsm.ssm_client.list_tags_for_resource(
                ResourceType="Parameter",
                ResourceId=self.name,
            )
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("TagList", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class SsmParameterSearcher(res_lib.Searcher[SsmParameter]):
    pass


ssm_parameter_searcher = SsmParameterSearcher(
    # list resources
    service="ssm",
    method="describe_parameters",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 50}},
    result_path=res_lib.ResultPath("Parameters"),
    # extract document
    doc_class=SsmParameter,
    # search
    resource_type=SearcherEnum.ssm_parameter,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.NgramWordsField(name="type", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="tier", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.StoredField(name="param_arn"),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

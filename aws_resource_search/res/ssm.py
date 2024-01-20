# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

import sayt.api as sayt
import aws_arns.api as arns
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


@dataclasses.dataclass
class SsmParameter(rl.ResourceDocument):
    # fmt: off
    type: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="type", minsize=2, maxsize=4, stored=True)})
    tier: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="tier", minsize=2, maxsize=4, stored=True)})
    param_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="param_arn")})
    # fmt: on

    @property
    def last_modified_date(self) -> datetime:
        return rl.get_datetime(self.raw_data, "LastModifiedDate")

    @property
    def description(self) -> str:
        return rl.get_description(self.raw_data, "Description")

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
        return rl.format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            rl.format_key_value("type", self.type),
            rl.format_key_value("tier", self.tier),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.param_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.ssm.get_parameter(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.ssm.parameters

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.ssm_client.get_parameter(Name=self.name)
            param = res["Parameter"]
            detail_items.extend([
                from_detail("LastModifiedDate", self.raw_data.get("LastModifiedDate", "NA"), url=url),
                from_detail("Type", param.get("Type", "NA"), url=url),
                from_detail("Version", param.get("Version", "NA"), url=url),
                from_detail("DataType", param.get("DataType", "NA"), url=url),
                from_detail("Value", param.get("Value", "NA"), self.one_line(param.get("Value", "NA")), url=url),
            ])

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.ssm_client.list_tags_for_resource(
                ResourceType="Parameter",
                ResourceId=self.name,
            )
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class SsmParameterSearcher(rl.BaseSearcher[SsmParameter]):
    pass


ssm_parameter_searcher = SsmParameterSearcher(
    # list resources
    service="ssm",
    method="describe_parameters",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 50}},
    result_path=rl.ResultPath("Parameters"),
    # extract document
    doc_class=SsmParameter,
    # search
    resource_type=rl.SearcherEnum.ssm_parameter.value,
    fields=SsmParameter.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.ssm_parameter.value),
    more_cache_key=None,
)

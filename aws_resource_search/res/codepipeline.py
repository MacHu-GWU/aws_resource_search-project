# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value, ShortcutEnum, format_key, format_value

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class CodePipelinePipeline(res_lib.BaseDocument):
    version: int = dataclasses.field()
    update_at: datetime = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    pipeline_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            version=resource.get("version", "NA"),
            update_at=resource.get("updated", "NA"),
            id=resource["name"],
            name=resource["name"],
            pipeline_arn=arns.res.CodePipelinePipeline.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                name=resource["name"],
            ).to_arn(),
        )

    @property
    def title(self) -> str:
        return format_key_value("pipeline_name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.pipeline_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.codepipeline.get_pipeline(name_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)

        detail_items.extend([
            Item("version", self.version),
            Item("update_at", self.update_at),
        ])

        with self.enrich_details(detail_items):
            res = ars.bsm.codepipeline_client.get_pipeline(name=self.name)
            dct = res["pipeline"]
            roleArn = dct.get("roleArn", "NA")
            variables = dct.get("variables", [])
            detail_items.extend([
                Item("roleArn", roleArn, url=ars.aws_console.iam.get_role(roleArn)),
            ])
            for d in variables:
                name = d["name"]
                description = d["description"]
                defaultValue = d["defaultValue"]
                detail_items.append(
                    res_lib.DetailItem(
                        title="🎯 var = {}, default value = {}, ({})".format(
                            format_key(name),
                            format_value(defaultValue),
                            description,
                        ),
                        subtitle= f"📋 {ShortcutEnum.CTRL_A} to copy.",
                        uid=name,
                        variables={"copy": defaultValue, "url": None},
                    )
                )

        with self.enrich_details(detail_items):
            res = ars.bsm.codepipeline_client.list_tags_for_resource(resourceArn=self.arn)
            tags: dict = {dct["key"]: dct["value"] for dct in res.get("tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items
    # fmt: on


codepipeline_pipeline_searcher = res_lib.Searcher(
    # list resources
    service="codepipeline",
    method="list_pipelines",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {
            "MaxItems": 5000,
            "PageSize": 1000,
        },
    },
    result_path=res_lib.ResultPath("pipelines"),
    # extract document
    doc_class=CodePipelinePipeline,
    # search
    resource_type="codepipeline-pipeline",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="version"),
        res_lib.sayt.StoredField(name="update_at"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(
            name="name",
            minsize=2,
            maxsize=4,
            stored=True,
            sortable=True,
            ascending=True,
        ),
        res_lib.sayt.StoredField(name="pipeline_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

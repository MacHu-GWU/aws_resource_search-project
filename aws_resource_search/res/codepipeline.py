# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value, ShortcutEnum, format_key, format_value
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class CodePipelinePipeline(res_lib.BaseDocument):
    pipeline_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
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
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)
        
        with self.enrich_details(detail_items):
            res = ars.bsm.codepipeline_client.get_pipeline(name=self.name)
            dct = res["pipeline"]
            version = dct.get("version", 0)
            update_at = res_lib.get_none_or_default(dct, "metadata.updated", "NA")
            roleArn = dct.get("roleArn", "NA")
            variables = dct.get("variables", [])
            detail_items.extend([
                from_detail("version", version, url=url),
                from_detail("update_at", update_at, url=url),
                from_detail("roleArn", roleArn, url=ars.aws_console.iam.get_role(roleArn)),
            ])

            for d in variables:
                name = d["name"]
                description = d["description"]
                defaultValue = d["defaultValue"]
                detail_items.append(
                    res_lib.DetailItem.new(
                        title="🎯 var = {}, default value = {}, ({})".format(
                            format_key(name),
                            format_value(defaultValue),
                            description,
                        ),
                        subtitle=f"🌐 {ShortcutEnum.ENTER} to open url, 📋 {ShortcutEnum.CTRL_A} to copy var name.",
                        uid=f"var {name}",
                        copy=name,
                        url=url,
                    )
                )

        with self.enrich_details(detail_items):
            res = ars.bsm.codepipeline_client.list_tags_for_resource(resourceArn=self.arn)
            tags: dict = {dct["key"]: dct["value"] for dct in res.get("tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class CodePipelinePipelineSearcher(res_lib.Searcher[CodePipelinePipeline]):
    pass


codepipeline_pipeline_searcher = CodePipelinePipelineSearcher(
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
    resource_type=SearcherEnum.codepipeline_pipeline,
    fields=res_lib.define_fields(
        fields=[
            res_lib.sayt.StoredField(name="pipeline_arn"),
        ],
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

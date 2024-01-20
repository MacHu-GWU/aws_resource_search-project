# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

import sayt.api as sayt
import aws_arns.api as arns
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


@dataclasses.dataclass
class CodePipelinePipeline(rl.ResourceDocument):
    # fmt: off
    pipeline_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="pipeline_arn")})
    # fmt: on

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
        return rl.format_key_value("pipeline_name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.pipeline_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.codepipeline.get_pipeline(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.codepipeline.pipelines

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)
        
        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.codepipeline_client.get_pipeline(name=self.name)
            dct = res["pipeline"]
            version = dct.get("version", 0)
            update_at = rl.get_none_or_default(dct, "metadata.updated", "NA")
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
                    rl.DetailItem.new(
                        title="🎯 var = {}, default value = {}, ({})".format(
                            rl.format_key(name),
                            rl.format_value(defaultValue),
                            description,
                        ),
                        subtitle=f"🌐 {rl.ShortcutEnum.ENTER} to open url, 📋 {rl.ShortcutEnum.CTRL_A} to copy var name.",
                        uid=f"var {name}",
                        copy=name,
                        url=url,
                    )
                )

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.codepipeline_client.list_tags_for_resource(resourceArn=self.arn)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class CodePipelinePipelineSearcher(rl.BaseSearcher[CodePipelinePipeline]):
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
    result_path=rl.ResultPath("pipelines"),
    # extract document
    doc_class=CodePipelinePipeline,
    # search
    resource_type=rl.SearcherEnum.codepipeline_pipeline.value,
    fields=CodePipelinePipeline.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(
        rl.SearcherEnum.codepipeline_pipeline.value
    ),
    more_cache_key=None,
)

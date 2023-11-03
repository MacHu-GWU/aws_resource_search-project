# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value, ShortcutEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class CodeBuildProject(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    project_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource,
            name=resource,
            project_arn=arns.res.CodeBuildProject.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                name=resource,
            ).to_arn(),
        )

    @property
    def title(self) -> str:
        return format_key_value("project_name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.project_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.codebuild.get_project(project_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)

        with self.enrich_details(detail_items):
            res = ars.bsm.codebuild_client.batch_get_projects(names=[self.name])
            dct = res["projects"][0]
            description = dct.get("description", "NA")
            serviceRole = dct.get("serviceRole", "NA")
            concurrentBuildLimit = dct.get("concurrentBuildLimit", "NA")
            timeoutInMinutes = dct.get("timeoutInMinutes", "NA")
            queuedTimeoutInMinutes = dct.get("queuedTimeoutInMinutes", "NA")
            resourceAccessRole = dct.get("resourceAccessRole", "NA")
            source_type = dct.get("source", {}).get("type", "NA")
            source_location = dct.get("source", {}).get("location", "NA")
            source_buildspec = dct.get("source", {}).get("buildspec", "NA")
            environment_type = dct.get("environment", {}).get("type", "NA")
            environment_image = dct.get("environment", {}).get("image", "NA")
            environment_computeType = dct.get("environment", {}).get("computeType", "NA")
            environment_privilegedMode = dct.get("environment", {}).get("privilegedMode", "NA")
            env_vars = dct.get("environment", {}).get("environmentVariables", [])
            detail_items.extend([
                Item("description", description),
                Item("serviceRole", serviceRole, url=ars.aws_console.iam.get_role(serviceRole)),
                Item("concurrentBuildLimit", concurrentBuildLimit),
                Item("timeoutInMinutes", timeoutInMinutes),
                Item("queuedTimeoutInMinutes", queuedTimeoutInMinutes),
                Item("resourceAccessRole", resourceAccessRole, url=ars.aws_console.iam.get_role(serviceRole)),
                Item("source_type", source_type),
                Item("source_location", source_location),
                Item("source_buildspec", source_buildspec, self.one_line(source_buildspec)),
                Item("environment_type", environment_type),
                Item("environment_image", environment_image),
                Item("environment_computeType", environment_computeType),
                Item("environment_privilegedMode", environment_privilegedMode),
            ])
            for d in env_vars:
                name = d["name"]
                value = d["value"]
                type = d["type"]
                detail_items.append(
                    res_lib.DetailItem(
                        title="🎯 env var: {} ({})".format(
                            format_key_value(name, value),
                            type,
                        ),
                        subtitle= f"📋 {ShortcutEnum.CTRL_A} to copy.",
                        uid=name,
                        variables={"copy": value, "url": None},
                    )
                )
            tags: dict = {d["key"]: d["value"] for d in dct.get("tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items
    # fmt: on


codebuild_project_searcher = res_lib.Searcher(
    # list resources
    service="codebuild",
    method="list_projects",
    is_paginator=True,
    default_boto_kwargs={
        "sortBy": "NAME",
        "sortOrder": "ASCENDING",
        "PaginationConfig": {
            "MaxItems": 5000,
        },
    },
    result_path=res_lib.ResultPath("projects"),
    # extract document
    doc_class=CodeBuildProject,
    # search
    resource_type="codebuild-project",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(
            name="name",
            minsize=2,
            maxsize=4,
            stored=True,
            sortable=True,
            ascending=True,
        ),
        res_lib.sayt.StoredField(name="project_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

codebuild_run_status_icon_mapper = {
    "SUCCEEDED": "🟢",
    "FAILED": "🔴",
    "FAULT": "🔴",
    "TIMED_OUT": "🔴",
    "IN_PROGRESS": "🟡",
    "STOPPED": "🔴",
}


@dataclasses.dataclass
class CodeBuildJobRun(res_lib.BaseDocument):
    fullname: str = dataclasses.field()
    status: str = dataclasses.field()
    start_at: datetime = dataclasses.field()
    end_at: datetime = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    build_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        fullname = resource
        short_id = resource.split(":", 1)[1]
        return cls(
            raw_data=resource,
            fullname=fullname,
            status="NA",
            start_at="NA",
            end_at="NA",
            id=short_id,
            name=short_id,
            build_arn=arns.res.CodeBuildRun.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                fullname=fullname,
            ).to_arn(),
        )

    @classmethod
    def from_many_resources(
        cls,
        resources: res_lib.ResourceIterproxy,
        bsm,
        boto_kwargs,
    ):
        """
        We only pull the last 100 builds for each project.
        """
        ids = resources.all()[:100]
        if len(ids) == 0:
            return
        res = bsm.codebuild_client.batch_get_builds(ids=ids)
        for dct in res.get("builds", []):
            short_id = dct["id"].split(":", 1)[1]
            yield cls(
                raw_data=dct,
                fullname=dct["id"],
                status=dct["buildStatus"],
                start_at=dct.get("startTime"),
                end_at=dct.get("endTime"),
                id=short_id,
                name=short_id,
                build_arn=dct["arn"],
            )

    @property
    def status_icon(self):
        return codebuild_run_status_icon_mapper[self.status]

    @property
    def title(self) -> str:
        return format_key_value("build_id", self.id)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            f"{self.status_icon} {self.status}",
            format_key_value("start_at", self.start_at),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        project_name = self.fullname.split(":", 1)[0]
        return f"{project_name}@{self.id}"

    @property
    def arn(self) -> str:
        return self.build_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.codebuild.get_build_run(run_id_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        detail_items.extend([
            Item("status", self.status, text=f"{self.status_icon} {self.status}"),
            Item("start_at", self.start_at),
            Item("end_at", self.end_at),
        ])

        serviceRole = self.raw_data.get("serviceRole", "NA")
        source_buildspec = self.raw_data.get("source", {}).get("buildspec", "NA")
        initiator = self.raw_data.get("initiator", "NA")
        detail_items.extend([
            Item("serviceRole", serviceRole, url=ars.aws_console.iam.get_role(serviceRole)),
            Item("source_buildspec", source_buildspec, self.one_line(source_buildspec)),
            Item("initiator", initiator),
        ])

        env_vars = self.raw_data.get("environment", {}).get("environmentVariables", [])
        for d in env_vars:
            name = d["name"]
            value = d["value"]
            type = d["type"]
            detail_items.append(
                res_lib.DetailItem(
                    title="🎯 env var: {} ({})".format(
                        format_key_value(name, value),
                        type,
                    ),
                    subtitle=f"📋 {ShortcutEnum.CTRL_A} to copy.",
                    uid=name,
                    variables={"copy": value, "url": None},
                )
            )

        return detail_items
    # fmt: on


codebuild_job_run_searcher = res_lib.Searcher(
    # list resources
    service="codebuild",
    method="list_builds_for_project",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {
            "MaxItems": 100,
        },
    },
    result_path=res_lib.ResultPath("ids"),
    # extract document
    doc_class=CodeBuildJobRun,
    # search
    resource_type="codebuild-jobrun",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="fullname"),
        res_lib.sayt.StoredField(name="status"),
        res_lib.sayt.StoredField(name="start_at"),
        res_lib.sayt.StoredField(name="end_at"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="build_arn"),
    ],
    cache_expire=5 * 60,
    more_cache_key=None,
)

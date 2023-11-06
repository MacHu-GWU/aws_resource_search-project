# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value, ShortcutEnum
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


def make_env_var_item(
    name: str,
    value: str,
    type: str,
    url: str,
) -> res_lib.DetailItem:
    return res_lib.DetailItem.new(
        title="🎯 env var: {} ({})".format(
            format_key_value(name, value),
            type,
        ),
        subtitle=f"🌐 {ShortcutEnum.ENTER} to open url, 📋 {ShortcutEnum.CTRL_A} to copy value.",
        uid=f"env var {name}",
        copy=value,
        url=url,
    )


@dataclasses.dataclass
class CodeBuildProject(res_lib.BaseDocument):
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
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.codebuild_client.batch_get_projects(names=[self.name])
            projects = res.get("projects", [])
            if len(projects) == 0:
                return [
                    res_lib.DetailItem.new(
                        title="🚨 Project not found, maybe it's deleted?",
                        subtitle=f"{ShortcutEnum.ENTER} to verify in AWS Console",
                        url=self.get_console_url(ars.aws_console),
                    )
                ]
            dct = projects[0]
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
                from_detail("description", description, url=url),
                from_detail("serviceRole", serviceRole, url=ars.aws_console.iam.get_role(serviceRole)),
                from_detail("concurrentBuildLimit", concurrentBuildLimit, url=url),
                from_detail("timeoutInMinutes", timeoutInMinutes, url=url),
                from_detail("queuedTimeoutInMinutes", queuedTimeoutInMinutes, url=url),
                from_detail("resourceAccessRole", resourceAccessRole, url=ars.aws_console.iam.get_role(serviceRole)),
                from_detail("source_type", source_type, url=url),
                from_detail("source_location", source_location, url=url),
                from_detail("source_buildspec", source_buildspec, self.one_line(source_buildspec), url=url),
                from_detail("environment_type", environment_type, url=url),
                from_detail("environment_image", environment_image, url=url),
                from_detail("environment_computeType", environment_computeType, url=url),
                from_detail("environment_privilegedMode", environment_privilegedMode, url=url),
            ])
            for d in env_vars:
                item = make_env_var_item(d["name"], d["value"], d["type"], url)
                detail_items.append(item)
            tags: dict = {d["key"]: d["value"] for d in dct.get("tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url=url))

        return detail_items
    # fmt: on


class CodeBuildProjectSearcher(res_lib.Searcher[CodeBuildProject]):
    pass


codebuild_project_searcher = CodeBuildProjectSearcher(
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
    resource_type=SearcherEnum.codebuild_project,
    fields=res_lib.define_fields(
        fields=[
            res_lib.sayt.StoredField(name="project_arn"),
        ],
    ),
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
    status: str = dataclasses.field()

    @property
    def fullname(self) -> str:
        return self.raw_data["id"]

    @property
    def short_id(self) -> int:
        return int(self.raw_data["id"].split(":", 1)[1])

    @property
    def start_at(self) -> datetime:
        return res_lib.get_datetime(self.raw_data, "startTime")

    @property
    def end_at(self) -> datetime:
        return res_lib.get_datetime(self.raw_data, "endTime")

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
                id=short_id,
                name=short_id,
                status=dct["buildStatus"],
            )

    @property
    def title(self) -> str:
        return format_key_value("build_id", self.id)

    @property
    def subtitle(self) -> str:
        utc_now = res_lib.get_utc_now()
        if self.raw_data.get("endTime"):
            duration = int((self.end_at - self.start_at).total_seconds())
            completed = int((utc_now - self.end_at).total_seconds())
            completed = res_lib.human_readable_elapsed(completed)
        else:
            duration = int((utc_now - self.start_at).total_seconds())
            completed = "Not yet"
        duration = res_lib.human_readable_elapsed(duration)
        status_icon = codebuild_run_status_icon_mapper[self.status]
        return "{}, {}, {}, {}".format(
            f"{status_icon} {self.status}",
            format_key_value("duration", duration),
            format_key_value("completed", completed),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        project_name = self.fullname.split(":", 1)[0]
        return f"{project_name}@{self.id}"

    @property
    def arn(self) -> str:
        return self.raw_data["arn"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.codebuild.get_build_run(run_id_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.codebuild_client.batch_get_builds(ids=[self.fullname])
            builds = res.get("builds", [])
            if len(builds) == 0:
                return [
                    res_lib.DetailItem.new(
                        title="🚨 build job run not found, maybe it's deleted?",
                        subtitle=f"{ShortcutEnum.ENTER} to verify in AWS Console",
                        url=url,
                    )
                ]
            build = builds[0]
            run = CodeBuildJobRun(raw_data=build, id=self.id, name=self.name)
            status_icon = codebuild_run_status_icon_mapper[run.status]
            detail_items.extend([
                from_detail("status", run.status, f"{status_icon} {run.status}", url=url),
                from_detail("start_at", run.start_at, url=url),
                from_detail("end_at", run.end_at, url=url),
            ])

        serviceRole = self.raw_data.get("serviceRole", "NA")
        source_buildspec = self.raw_data.get("source", {}).get("buildspec", "NA")
        initiator = self.raw_data.get("initiator", "NA")
        detail_items.extend([
            from_detail("serviceRole", serviceRole, url=ars.aws_console.iam.get_role(serviceRole)),
            from_detail("source_buildspec", source_buildspec, self.one_line(source_buildspec), url=url),
            from_detail("initiator", initiator, url=url),
        ])

        env_vars = self.raw_data.get("environment", {}).get("environmentVariables", [])
        for d in env_vars:
            item = make_env_var_item(d["name"], d["value"], d["type"], url)
            detail_items.append(item)

        return detail_items
    # fmt: on


class CodeBuildJobRunSearcher(res_lib.Searcher):
    pass


codebuild_job_run_searcher = CodeBuildJobRunSearcher(
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
    resource_type=SearcherEnum.codebuild_job_run,
    fields=res_lib.define_fields(
        fields=[
            res_lib.sayt.NgramWordsField(
                name="status",
                minsize=2,
                maxsize=4,
                stored=True,
            ),
        ],
        name_ascending=False,
    ),
    cache_expire=5 * 60,
    more_cache_key=None,
)

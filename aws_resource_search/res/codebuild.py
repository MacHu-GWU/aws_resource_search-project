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


def make_env_var_item(
    name: str,
    value: str,
    type: str,
    url: str,
) -> rl.DetailItem:
    return rl.DetailItem.new(
        title="🎯 env var: {} ({})".format(
            rl.format_key_value(name, value),
            type,
        ),
        subtitle=f"🌐 {rl.ShortcutEnum.ENTER} to open url, 📋 {rl.ShortcutEnum.CTRL_A} to copy value.",
        uid=f"env var {name}",
        copy=value,
        url=url,
    )


@dataclasses.dataclass
class CodeBuildProject(rl.ResourceDocument):
    # fmt: off
    project_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="project_arn")})
    # fmt: on

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
        return rl.format_key_value("project_name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.project_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.codebuild.get_project(project_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.codebuild.build_projects

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.codebuild_client.batch_get_projects(names=[self.name])
            projects = res.get("projects", [])
            if len(projects) == 0:
                return [
                    rl.DetailItem.new(
                        title="🚨 Project not found, maybe it's deleted?",
                        subtitle=f"{rl.ShortcutEnum.ENTER} to verify in AWS Console",
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
                from_detail("source_buildspec", source_buildspec, value_text=self.one_line(source_buildspec), url=url),
                from_detail("environment_type", environment_type, url=url),
                from_detail("environment_image", environment_image, url=url),
                from_detail("environment_computeType", environment_computeType, url=url),
                from_detail("environment_privilegedMode", environment_privilegedMode, url=url),
            ])
            for d in env_vars:
                item = make_env_var_item(d["name"], d["value"], d["type"], url)
                detail_items.append(item)

            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url=url))

        return detail_items
    # fmt: on


class CodeBuildProjectSearcher(rl.BaseSearcher[CodeBuildProject]):
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
    result_path=rl.ResultPath("projects"),
    # extract document
    doc_class=CodeBuildProject,
    # search
    resource_type=rl.SearcherEnum.codebuild_project.value,
    fields=CodeBuildProject.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.codebuild_project.value),
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
class CodeBuildJobRun(rl.ResourceDocument):
    # fmt: off
    status: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="status", minsize=2, maxsize=4, stored=True)})
    # fmt: on

    @property
    def fullname(self) -> str:
        return self.raw_data["id"]

    @property
    def short_id(self) -> int:
        return int(self.raw_data["id"].split(":", 1)[1])

    @property
    def start_at(self) -> datetime:
        return rl.get_datetime(self.raw_data, "startTime")

    @property
    def end_at(self) -> datetime:
        return rl.get_datetime(self.raw_data, "endTime")

    @classmethod
    def from_many_resources(
        cls,
        resources: rl.ResourceIterproxy,
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
        return rl.format_key_value("build_id", self.id)

    @property
    def subtitle(self) -> str:
        utc_now = rl.get_utc_now()
        if self.raw_data.get("endTime"):
            duration = int((self.end_at - self.start_at).total_seconds())
            completed = int((utc_now - self.end_at).total_seconds())
            completed = rl.to_human_readable_elapsed(completed)
        else:
            duration = int((utc_now - self.start_at).total_seconds())
            completed = "Not yet"
        duration = rl.to_human_readable_elapsed(duration)
        status_icon = codebuild_run_status_icon_mapper[self.status]
        return "{}, {}, {}, {}".format(
            f"{status_icon} {self.status}",
            rl.format_key_value("duration", duration),
            rl.format_key_value("completed", completed),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        project_name = self.fullname.split(":", 1)[0]
        return f"{project_name}@{self.id}"

    @property
    def arn(self) -> str:
        return self.raw_data["arn"]

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.codebuild.get_build_run(run_id_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.codebuild_client.batch_get_builds(ids=[self.fullname])
            builds = res.get("builds", [])
            if len(builds) == 0:
                return [
                    rl.DetailItem.new(
                        title="🚨 build job run not found, maybe it's deleted?",
                        subtitle=f"{rl.ShortcutEnum.ENTER} to verify in AWS Console",
                        url=url,
                    )
                ]
            build = builds[0]
            run = CodeBuildJobRun(raw_data=build, id=self.id, name=self.name, status=build["buildStatus"])
            status_icon = codebuild_run_status_icon_mapper[run.status]
            detail_items.extend([
                from_detail("status", run.status, value_text=f"{status_icon} {run.status}", url=url),
                from_detail("start_at", run.start_at, url=url),
                from_detail("end_at", run.end_at, url=url),
            ])

        serviceRole = self.raw_data.get("serviceRole", "NA")
        source_buildspec = self.raw_data.get("source", {}).get("buildspec", "NA")
        initiator = self.raw_data.get("initiator", "NA")
        detail_items.extend([
            from_detail("serviceRole", serviceRole, url=ars.aws_console.iam.get_role(serviceRole)),
            from_detail("source_buildspec", source_buildspec, value_text=self.one_line(source_buildspec), url=url),
            from_detail("initiator", initiator, url=url),
        ])

        env_vars = self.raw_data.get("environment", {}).get("environmentVariables", [])
        for d in env_vars:
            item = make_env_var_item(d["name"], d["value"], d["type"], url)
            detail_items.append(item)

        return detail_items
    # fmt: on


class CodeBuildJobRunSearcher(rl.BaseSearcher):
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
    result_path=rl.ResultPath("ids"),
    # extract document
    doc_class=CodeBuildJobRun,
    # search
    resource_type=rl.SearcherEnum.codebuild_job_run.value,
    fields=CodeBuildJobRun.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.codebuild_job_run.value),
    more_cache_key=None,
)

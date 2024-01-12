# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class EcsCluster(res_lib.BaseDocument):
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        ecs_cluster = arns.res.EcsCluster.from_arn(resource)
        return cls(
            raw_data=resource,
            id=ecs_cluster.cluster_name,
            name=ecs_cluster.cluster_name,
        )

    @property
    def title(self) -> str:
        return format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}".format(
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.ecs.get_cluster_services(name_or_arn=self.arn)

    @property
    def cluster_name(self) -> str:
        return self.name

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.ecs_client.describe_clusters(
                clusters=[self.arn],
                include=["TAGS"],
            )
            dct = res.get("clusters", [None])[0]
            if dct:
                detail_items.extend(
                    # fmt: off
                    [
                        from_detail("cluster_name", dct["clusterName"], url=url),
                        from_detail("cluster_arn", dct["clusterArn"], url=url),
                        from_detail("status", dct["status"], url=url),
                        from_detail("running_task_count", dct["runningTasksCount"], url=url),
                        from_detail("pending_task_count", dct["pendingTasksCount"], url=url),
                        from_detail("pending_task_count", dct["pendingTasksCount"], url=url),
                        from_detail("active_service_count", dct["activeServicesCount"], url=url),
                        from_detail("registered_container_instances_count", dct["registeredContainerInstancesCount"], url=url),
                    ]
                    # fmt: on
                )
                tags: dict = {dct["key"]: dct["value"] for dct in dct.get("tags", [])}
                detail_items.extend(res_lib.DetailItem.from_tags(tags, url=url))
        return detail_items


class EcsClusterSearcher(res_lib.Searcher[EcsCluster]):
    pass


ecs_cluster_searcher = EcsClusterSearcher(
    # list resources
    service="ecs",
    method="list_clusters",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 100}},
    result_path=res_lib.ResultPath("clusterArns"),
    # extract document
    doc_class=EcsCluster,
    # search
    resource_type=SearcherEnum.ecs_cluster,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class EcsTaskRun(res_lib.BaseDocument):
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        task_run = arns.res.EcsTaskRun.from_arn(resource)
        return cls(
            raw_data=resource,
            id=task_run.short_id,
            name=task_run.short_id,
        )

    @property
    def title(self) -> str:
        return format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}".format(
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return f"{self.cluster_name}@{self.name}"

    @property
    def arn(self) -> str:
        return self.raw_data

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.ecs.get_task_run_configuration(
            task_short_id_or_arn=self.arn, cluster_name=None
        )

    @property
    def cluster_name(self) -> str:
        task_run = arns.res.EcsTaskRun.from_arn(self.arn)
        return task_run.cluster_name

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.ecs_client.describe_tasks(
                cluster=self.cluster_name,
                tasks=[self.arn],
                include=["TAGS"],
            )
            task_dct = res.get("tasks", [None])[0]
            task_definition_arn = None
            if task_dct:
                task_definition_arn = task_dct["taskDefinitionArn"]
                detail_items.extend(
                    # fmt: off
                    [
                        from_detail("cluster_name", self.cluster_name, url=ars.aws_console.ecs.get_cluster_tasks(name_or_arn=task_dct["clusterArn"])),
                        from_detail("task_definition_arn", task_definition_arn, url=ars.aws_console.ecs.get_task_definition_revision_containers(name_or_arn=task_definition_arn)),
                        from_detail("platform_family", task_dct.get("platformFamily", "NA"), url=url),
                        from_detail("platform_version", task_dct.get("platformVersion", "NA"), url=url),
                        from_detail("cpu", task_dct.get("cpu", "NA"), url=url),
                        from_detail("memory", task_dct.get("memory", "NA"), url=url),
                        from_detail("ephemeral_storage", task_dct.get("ephemeralStorage", {}).get("sizeInGiB", "NA"), url=url),
                        from_detail("started_at", task_dct.get("startedAt", "NA"), url=url),
                        from_detail("stopped_at", task_dct.get("stoppedAt", "NA"), url=url),
                        from_detail("started_by", task_dct.get("startedBy", "NA"), url=url),
                        from_detail("stop_code", task_dct.get("stopCode", "NA"), url=url),
                        from_detail("stopped_reason", task_dct.get("stoppedReason", "NA"), url=url),
                        from_detail("connectivity", task_dct.get("connectivity", "NA"), url=url),
                        from_detail("connectivity_at", task_dct.get("connectivityAt", "NA"), url=url),
                        from_detail("health_status", task_dct.get("healthStatus", "NA"), url=url),
                        from_detail("desired_status", task_dct.get("desiredStatus", "NA"), url=url),
                        from_detail("last_status", task_dct.get("lastStatus", "NA"), url=url),
                        from_detail("launch_type", task_dct.get("launchType", "NA"), url=url),
                    ]
                    # fmt: on
                )

            if task_definition_arn is not None:
                res = ars.bsm.ecs_client.describe_task_definition(
                    taskDefinition=task_definition_arn,
                    include=["TAGS"],
                )
                task_def_dct = res.get("taskDefinition", None)
                if task_def_dct:
                    detail_items.extend(
                        # fmt: off
                        [
                            from_detail("task_role_arn", task_def_dct["taskRoleArn"], url=ars.aws_console.iam.get_role(task_def_dct["taskRoleArn"])),
                            from_detail("task_execution_role_arn", task_def_dct["executionRoleArn"], url=ars.aws_console.iam.get_role(task_def_dct["executionRoleArn"])),
                        ]
                        # fmt: on
                    )

            if task_dct:
                tags: dict = {
                    dct["key"]: dct["value"] for dct in task_dct.get("tags", [])
                }
                detail_items.extend(res_lib.DetailItem.from_tags(tags, url=url))

        return detail_items


class EcsTaskRunSearcher(res_lib.Searcher[EcsTaskRun]):
    pass


ecs_task_run_searcher = EcsTaskRunSearcher(
    # list resources
    service="ecs",
    method="list_tasks",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {"MaxItems": 9999, "PageSize": 100},
    },
    result_path=res_lib.ResultPath("taskArns"),
    # extract document
    doc_class=EcsTaskRun,
    # search
    resource_type=SearcherEnum.ecs_task_run,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class EcsTaskDefinitionFamily(res_lib.BaseDocument):
    v1_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        ecs_task_def = arns.res.EcsTaskDefinition.new(
            aws_account_id=bsm.aws_account_id,
            aws_region=bsm.aws_region,
            task_name=resource,
            version=1,
        )
        return cls(
            raw_data=resource,
            id=ecs_task_def.task_name,
            name=ecs_task_def.task_name,
            v1_arn=ecs_task_def.to_arn(),
        )

    @property
    def title(self) -> str:
        return format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}".format(
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.v1_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.ecs.get_task_definition_revisions(name_or_arn=self.v1_arn)

    @property
    def task_name(self) -> str:
        return self.name

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.ecs_client.list_task_definitions(
                familyPrefix=self.name,
                sort="DESC",
                maxResults=100,
            )
            arn_lst = res.get("taskDefinitionArns", None)
            if arn_lst:
                detail_items.extend(
                    # fmt: off
                    [
                        from_detail("task_definition_arn", arn, url=ars.aws_console.ecs.get_task_definition_revision_containers(name_or_arn=arn))
                        for arn in arn_lst
                    ]
                    # fmt: on
                )
        return detail_items


class EcsTaskDefinitionFamilySearcher(res_lib.Searcher[EcsTaskDefinitionFamily]):
    pass


ecs_task_definition_family_searcher = EcsTaskDefinitionFamilySearcher(
    # list resources
    service="ecs",
    method="list_task_definition_families",
    is_paginator=True,
    default_boto_kwargs={
        "status": "ACTIVE",
        "PaginationConfig": {"MaxItems": 9999, "PageSize": 100},
    },
    result_path=res_lib.ResultPath("families"),
    # extract document
    doc_class=EcsTaskDefinitionFamily,
    # search
    resource_type=SearcherEnum.ecs_task_definition_family,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.StoredField(name="v1_arn"),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

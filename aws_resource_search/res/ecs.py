# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import sayt.api as sayt
import aws_arns.api as arns
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


@dataclasses.dataclass
class EcsCluster(rl.ResourceDocument):
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
        return rl.format_key_value("name", self.name)

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

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.ecs.get_cluster_services(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.ecs.clusters

    @property
    def cluster_name(self) -> str:
        return self.name

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.ecs_client.describe_clusters(
                clusters=[self.arn],
                include=["TAGS"],
            )
            dct = res.get("clusters", [None])[0]
            if dct:
                detail_items.extend(
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
                )
                tags = rl.extract_tags(res)
                detail_items.extend(rl.DetailItem.from_tags(tags, url=url))
        return detail_items
    # fmt: on


class EcsClusterSearcher(rl.BaseSearcher[EcsCluster]):
    pass


ecs_cluster_searcher = EcsClusterSearcher(
    # list resources
    service="ecs",
    method="list_clusters",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 100}},
    result_path=rl.ResultPath("clusterArns"),
    # extract document
    doc_class=EcsCluster,
    # search
    resource_type=rl.SearcherEnum.ecs_cluster.value,
    fields=EcsCluster.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.ecs_cluster.value),
    more_cache_key=None,
)


@dataclasses.dataclass
class EcsTaskRun(rl.ResourceDocument):
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
        return rl.format_key_value("name", self.name)

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

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.ecs.get_task_run_configuration(
            task_short_id_or_arn=self.arn, cluster_name=None
        )

    @property
    def cluster_name(self) -> str:
        task_run = arns.res.EcsTaskRun.from_arn(self.arn)
        return task_run.cluster_name

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
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
                )

            if task_definition_arn is not None:
                res = ars.bsm.ecs_client.describe_task_definition(
                    taskDefinition=task_definition_arn,
                    include=["TAGS"],
                )
                task_def_dct = res.get("taskDefinition", None)
                if task_def_dct:
                    detail_items.extend(
                        [
                            from_detail("task_role_arn", task_def_dct["taskRoleArn"], url=ars.aws_console.iam.get_role(task_def_dct["taskRoleArn"])),
                            from_detail("task_execution_role_arn", task_def_dct["executionRoleArn"], url=ars.aws_console.iam.get_role(task_def_dct["executionRoleArn"])),
                        ]
                    )

            if task_dct:
                tags = rl.extract_tags(res)
                detail_items.extend(rl.DetailItem.from_tags(tags, url=url))

        return detail_items
    # fmt: on


class EcsTaskRunSearcher(rl.BaseSearcher[EcsTaskRun]):
    pass


ecs_task_run_searcher = EcsTaskRunSearcher(
    # list resources
    service="ecs",
    method="list_tasks",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {"MaxItems": 9999, "PageSize": 100},
    },
    result_path=rl.ResultPath("taskArns"),
    # extract document
    doc_class=EcsTaskRun,
    # search
    resource_type=rl.SearcherEnum.ecs_task_run.value,
    fields=EcsTaskRun.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.ecs_task_run.value),
    more_cache_key=None,
)


@dataclasses.dataclass
class EcsTaskDefinitionFamily(rl.ResourceDocument):
    # fmt: off
    v1_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="v1_arn")})
    # fmt: on

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
        return rl.format_key_value("name", self.name)

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

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.ecs.get_task_definition_revisions(name_or_arn=self.v1_arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.ecs.task_definitions

    @property
    def task_name(self) -> str:
        return self.name

    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
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


class EcsTaskDefinitionFamilySearcher(rl.BaseSearcher[EcsTaskDefinitionFamily]):
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
    result_path=rl.ResultPath("families"),
    # extract document
    doc_class=EcsTaskDefinitionFamily,
    # search
    resource_type=rl.SearcherEnum.ecs_task_definition_family.value,
    fields=EcsTaskDefinitionFamily.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(
        rl.SearcherEnum.ecs_task_definition_family.value
    ),
    more_cache_key=None,
)

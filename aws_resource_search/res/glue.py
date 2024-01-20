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


class GlueMixin:
    @property
    def description(self: rl.ResourceDocument) -> str:
        return rl.get_description(self.raw_data, "Description")


@dataclasses.dataclass
class GlueDatabase(rl.ResourceDocument, GlueMixin):
    # fmt: off
    database_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="database_arn")})
    # fmt: on

    @property
    def catalog_id(self) -> str:
        return self.raw_data["CatalogId"]

    @property
    def database(self) -> str:
        return self.raw_data["Name"]

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["Name"],
            name=resource["Name"],
            database_arn="arn:aws:glue:{aws_region}:{aws_account_id}:database/{database}".format(
                aws_region=bsm.aws_region,
                aws_account_id=bsm.aws_account_id,
                database=resource["Name"],
            ),
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("name", self.database)

    @property
    def subtitle(self) -> str:
        return "{}, {}".format(
            self.description,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.database_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.glue.get_database(database_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.glue.databases


class GlueDatabaseSearcher(rl.BaseSearcher[GlueDatabase]):
    pass


glue_database_searcher = GlueDatabaseSearcher(
    # list resources
    service="glue",
    method="get_databases",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("DatabaseList"),
    # extract document
    doc_class=GlueDatabase,
    # search
    resource_type=rl.SearcherEnum.glue_database.value,
    fields=GlueDatabase.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.glue_database.value),
    more_cache_key=None,
)


@dataclasses.dataclass
class GlueTable(rl.ResourceDocument, GlueMixin):
    # fmt: off
    table_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="table_arn")})
    # fmt: on

    @property
    def catalog_id(self) -> str:
        return self.raw_data["CatalogId"]

    @property
    def database(self) -> str:
        return self.raw_data["DatabaseName"]

    @property
    def table(self) -> str:
        return self.raw_data["Name"]

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id="{}.{}".format(resource["DatabaseName"], resource["Name"]),
            name="{}.{}".format(resource["DatabaseName"], resource["Name"]),
            table_arn="arn:aws:glue:{aws_region}:{aws_account_id}:table/{database}/{table}".format(
                aws_region=bsm.aws_region,
                aws_account_id=bsm.aws_account_id,
                database=resource["DatabaseName"],
                table=resource["Name"],
            ),
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("fullname", f"{self.database}.{self.table}")

    @property
    def subtitle(self) -> str:
        return "{}, {}".format(
            self.description,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return f"{self.database}@{self.table}"

    @property
    def arn(self) -> str:
        return self.table_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.glue.get_table(table_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.glue.tables


class GlueTableSearcher(rl.BaseSearcher[GlueTable]):
    pass


glue_table_searcher = GlueTableSearcher(
    # list resources
    service="glue",
    method="get_tables",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("TableList"),
    # extract document
    doc_class=GlueTable,
    # search
    resource_type=rl.SearcherEnum.glue_database_table.value,
    fields=GlueTable.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.glue_database_table.value),
    more_cache_key=lambda boto_kwargs: [boto_kwargs["DatabaseName"]],
)


@dataclasses.dataclass
class GlueJob(rl.ResourceDocument, GlueMixin):
    # fmt: off
    job_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="job_arn")})
    # fmt: on

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["Name"],
            name=resource["Name"],
            job_arn="arn:aws:glue:{aws_region}:{aws_account_id}:job/{job}".format(
                aws_region=bsm.aws_region,
                aws_account_id=bsm.aws_account_id,
                job=resource["Name"],
            ),
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}".format(
            self.description,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.job_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.glue.get_job(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.glue.jobs

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.glue_client.get_job(JobName=self.name)
            job_dct = res["Job"]
            description = job_dct.get("Description", "NA")
            role_arn = job_dct["Role"]
            glue_version = job_dct.get("GlueVersion", "NA")
            worker_type = job_dct.get("WorkerType", "NA")
            number_of_workers = job_dct.get("NumberOfWorkers", "NA")
            max_concurrent_runs = job_dct.get("ExecutionProperty", {}).get("MaxConcurrentRuns", "unknown")
            max_retries = job_dct.get("MaxRetries", "NA")
            execution_class = job_dct.get("ExecutionClass", "NA")
            script_location = job_dct.get("Command", {}).get("ScriptLocation", "NA")

            detail_items.extend([
                from_detail("description", description, url=url),
                from_detail("role_arn", role_arn, url=ars.aws_console.iam.get_role(role_arn)),
                from_detail("glue_version", glue_version, url=url),
                from_detail("worker_type", worker_type, url=url),
                from_detail("number_of_workers", number_of_workers, url=url),
                from_detail("max_concurrent_runs", max_concurrent_runs, url=url),
                from_detail("max_retries", max_retries, url=url),
                from_detail("execution_class", execution_class, url=url),
                from_detail("script_location", script_location, url=ars.aws_console.s3.get_console_url(uri_liked=script_location)),
            ])

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.glue_client.get_tags(ResourceArn=self.arn)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class GlueJobSearcher(rl.BaseSearcher[GlueJob]):
    pass


glue_job_searcher = GlueJobSearcher(
    # list resources
    service="glue",
    method="get_jobs",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("Jobs"),
    # extract document
    doc_class=GlueJob,
    # search
    resource_type=rl.SearcherEnum.glue_job.value,
    fields=GlueJob.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.glue_job.value),
    more_cache_key=None,
)


glue_job_run_state_icon_mapper = {
    "STARTING": "🟡",
    "RUNNING": "🔵",
    "STOPPING": "🟡",
    "STOPPED": "⚫",
    "SUCCEEDED": "🟢",
    "FAILED": "🔴",
    "TIMEOUT": "🔴",
    "ERROR": "🔴",
    "WAITING'": "🟡",
}


@dataclasses.dataclass
class GlueJobRun(rl.ResourceDocument):
    # fmt: off
    started_on: datetime = dataclasses.field(metadata={"field": sayt.DatetimeField(name="started_on", sortable=True, ascending=False, stored=True)})
    # fmt: on

    @property
    def job_name(self) -> str:
        return self.raw_data["JobName"]

    @property
    def state(self) -> str:
        return self.raw_data["JobRunState"]

    @property
    def completed_on(self) -> datetime:
        return self.raw_data.get("CompletedOn")

    @property
    def execution_time(self) -> int:
        return self.raw_data.get("ExecutionTime")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            started_on=resource.get("StartedOn"),
            id=resource["Id"],
            name=resource["Id"],
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("job_run_id", self.id)

    @property
    def subtitle(self) -> str:
        state_icon = glue_job_run_state_icon_mapper[self.state]
        return "{} | {} | {} | {}, {}".format(
            f"{state_icon} {self.state}",
            rl.format_key_value("start", str(self.started_on)[:19]),
            rl.format_key_value("end", str(self.completed_on)[:19]),
            rl.format_key_value("elapsed", f"{self.execution_time} secs"),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return f"{self.job_name}@{self.id}"

    @property
    def arn(self) -> str:
        raise NotImplementedError("Glue Job Run does not have an ARN")

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.glue.get_glue_job_run(
            job_name_or_arn=self.job_name, job_run_id=self.id
        )

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = [
            from_detail("job_run_id", self.id, url=url),
        ]

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.glue_client.get_job_run(
                JobName=self.job_name,
                RunId=self.id,
            )
            dct = res["JobRun"]

            error_message = dct.get("ErrorMessage", "NA")
            log_group_name = dct.get("LogGroupName", "NA")

            detail_items.extend([
                from_detail("error_message", error_message, url=url),
                from_detail("output_logs", log_group_name, url=ars.aws_console.cloudwatch.get_log_stream(stream_name_or_arn=self.id, group_name=f"{log_group_name}/output")),
                from_detail("error_logs", log_group_name, url=ars.aws_console.cloudwatch.get_log_stream(stream_name_or_arn=self.id, group_name=f"{log_group_name}/error")),
            ])

            args = dct.get("Arguments", {})
            detail_items.extend(
                [
                    rl.DetailItem.new(
                        title=f"📝 arg: {rl.format_key_value(k, v)}",
                        subtitle=f"🌐 {rl.ShortcutEnum.ENTER} to open url, 📋 {rl.ShortcutEnum.CTRL_A} to copy arg value.",
                        uid=f"arg {k}",
                        copy=v,
                        url=url,
                    )
                    for k, v in args.items()
                ]
            )
            if len(args) == 0:
                detail_items.append(
                    rl.DetailItem.new(
                        title=f"📝 arg: 🔴 No arg found",
                        subtitle=f"no arg found",
                        uid=f"no arg found",
                        url=url,
                    )
                )

        return detail_items
    # fmt: on


class GlueJobRunSearcher(rl.BaseSearcher[GlueJobRun]):
    pass


glue_job_run_searcher = GlueJobRunSearcher(
    # list resources
    service="glue",
    method="get_job_runs",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 200}},
    result_path=rl.ResultPath("JobRuns"),
    # extract document
    doc_class=GlueJobRun,
    # search
    resource_type=rl.SearcherEnum.glue_job_run.value,
    fields=GlueJobRun.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.glue_job_run.value),
    more_cache_key=lambda boto_kwargs: [boto_kwargs["JobName"]],
)

glue_crawler_state_icon_mapper = {
    "READY": "🔵",
    "RUNNING": "🟢",
    "STOPPING": "🔴",
}


@dataclasses.dataclass
class GlueCrawler(rl.ResourceDocument, GlueMixin):
    # fmt: off
    crawler_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="crawler_arn")})
    # fmt: on

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["Name"],
            name=resource["Name"],
            crawler_arn=arns.res.GlueCrawler.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                name=resource["Name"],
            ).to_arn(),
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.crawler_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.glue.get_crawler(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.glue.crawlers

    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.glue_client.get_crawler(Name=self.name)
            dct = res["Crawler"]

            description = dct.get("Description", "NA")
            state = dct.get("State", "NA")
            role_arn = dct["Role"]
            if not role_arn.startswith("arn:"):
                role_arn = arns.res.IamRole.new(
                    aws_account_id=ars.bsm.aws_account_id,
                    name=role_arn,
                ).to_arn()

            state_icon = glue_crawler_state_icon_mapper[state]
            # fmt: off
            detail_items.extend([
                from_detail("description", description, url=url),
                from_detail("state", state, f"{state_icon} {state}", url=url),
                from_detail("role_arn", role_arn, url=ars.aws_console.iam.get_role(role_arn)),
            ])
            # fmt: on

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.glue_client.get_tags(ResourceArn=self.arn)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items


class GlueCrawlerSearcher(rl.BaseSearcher[GlueCrawler]):
    pass


glue_crawler_searcher = GlueCrawlerSearcher(
    # list resources
    service="glue",
    method="get_crawlers",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("Crawlers"),
    # extract document
    doc_class=GlueCrawler,
    # search
    resource_type=rl.SearcherEnum.glue_crawler.value,
    fields=GlueCrawler.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.glue_crawler.value),
    more_cache_key=None,
)

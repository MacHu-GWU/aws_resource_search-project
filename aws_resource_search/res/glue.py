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


class GlueMixin:
    @property
    def description(self: res_lib.BaseDocument) -> str:
        return res_lib.get_description(self.raw_data, "Description")


@dataclasses.dataclass
class GlueDatabase(res_lib.BaseDocument, GlueMixin):
    database_arn: str = dataclasses.field()

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
        return format_key_value("name", self.database)

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

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.glue.get_database(database_or_arn=self.arn)


class GlueDatabaseSearcher(res_lib.Searcher[GlueDatabase]):
    pass


glue_database_searcher = GlueDatabaseSearcher(
    # list resources
    service="glue",
    method="get_databases",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("DatabaseList"),
    # extract document
    doc_class=GlueDatabase,
    # search
    resource_type=SearcherEnum.glue_database,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.StoredField(name="database_arn"),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class GlueTable(res_lib.BaseDocument, GlueMixin):
    table_arn: str = dataclasses.field()

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
        return format_key_value("fullname", f"{self.database}.{self.table}")

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

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.glue.get_table(table_or_arn=self.arn)


class GlueTableSearcher(res_lib.Searcher[GlueTable]):
    pass


glue_table_searcher = GlueTableSearcher(
    # list resources
    service="glue",
    method="get_tables",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("TableList"),
    # extract document
    doc_class=GlueTable,
    # search
    resource_type=SearcherEnum.glue_database_table,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.StoredField(name="table_arn"),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=lambda boto_kwargs: [boto_kwargs["DatabaseName"]],
)


@dataclasses.dataclass
class GlueJob(res_lib.BaseDocument, GlueMixin):
    job_arn: str = dataclasses.field()

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
        return format_key_value("name", self.name)

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

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.glue.get_job(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.glue_client.get_job(JobName=self.name)
            job_dct = res["Job"]
            # fmt: off
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
            # fmt: on

        with self.enrich_details(detail_items):
            res = ars.bsm.glue_client.get_tags(ResourceArn=self.arn)
            tags: dict = res.get("Tags", {})
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

        return detail_items


class GlueJobSearcher(res_lib.Searcher[GlueJob]):
    pass


glue_job_searcher = GlueJobSearcher(
    # list resources
    service="glue",
    method="get_jobs",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Jobs"),
    # extract document
    doc_class=GlueJob,
    # search
    resource_type=SearcherEnum.glue_job,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.StoredField(name="job_arn"),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
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
class GlueJobRun(res_lib.BaseDocument):
    started_on: datetime = dataclasses.field()

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
        return format_key_value("job_run_id", self.id)

    @property
    def subtitle(self) -> str:
        state_icon = glue_job_run_state_icon_mapper[self.state]
        return "{} | {} | {} | {}, {}".format(
            f"{state_icon} {self.state}",
            format_key_value("start", str(self.started_on)[:19]),
            format_key_value("end", str(self.completed_on)[:19]),
            format_key_value("elapsed", f"{self.execution_time} secs"),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return f"{self.job_name}@{self.id}"

    @property
    def arn(self) -> str:
        raise NotImplementedError("Glue Job Run does not have an ARN")

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.glue.get_glue_job_run(
            job_name_or_arn=self.job_name, job_run_id=self.id
        )

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        url = self.get_console_url(ars.aws_console)
        detail_items = [
            from_detail("job_run_id", self.id, url=url),
        ]

        with self.enrich_details(detail_items):
            res = ars.bsm.glue_client.get_job_run(
                JobName=self.job_name,
                RunId=self.id,
            )
            dct = res["JobRun"]

            error_message = dct.get("ErrorMessage", "NA")
            log_group_name = dct.get("LogGroupName", "NA")

            # fmt: off
            detail_items.extend([
                from_detail("error_message", error_message, url=url),
                from_detail("output_logs", log_group_name, url=ars.aws_console.cloudwatch.get_log_stream(stream_name_or_arn=self.id, group_name=f"{log_group_name}/output")),
                from_detail("error_logs", log_group_name, url=ars.aws_console.cloudwatch.get_log_stream(stream_name_or_arn=self.id, group_name=f"{log_group_name}/error")),
            ])
            # fmt: on

            args = dct.get("Arguments", {})
            detail_items.extend(
                [
                    res_lib.DetailItem.new(
                        title=f"📝 arg: {format_key_value(k, v)}",
                        subtitle=f"🌐 {ShortcutEnum.ENTER} to open url, 📋 {ShortcutEnum.CTRL_A} to copy arg value.",
                        uid=f"arg {k}",
                        copy=v,
                        url=url,
                    )
                    for k, v in args.items()
                ]
            )
            if len(args) == 0:
                detail_items.append(
                    res_lib.DetailItem.new(
                        title=f"📝 arg: 🔴 No arg found",
                        subtitle=f"no arg found",
                        uid=f"no arg found",
                        url=url,
                    )
                )

        return detail_items


class GlueJobRunSearcher(res_lib.Searcher[GlueJobRun]):
    pass


glue_job_run_searcher = GlueJobRunSearcher(
    # list resources
    service="glue",
    method="get_job_runs",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 200}},
    result_path=res_lib.ResultPath("JobRuns"),
    # extract document
    doc_class=GlueJobRun,
    # search
    resource_type=SearcherEnum.glue_job_run,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.DatetimeField(name="started_on", sortable=True, ascending=False, stored=True),
        ],
        name_sortable=False,
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=lambda boto_kwargs: [boto_kwargs["JobName"]],
)

glue_crawler_state_icon_mapper = {
    "READY": "🔵",
    "RUNNING": "🟢",
    "STOPPING": "🔴",
}


@dataclasses.dataclass
class GlueCrawler(res_lib.BaseDocument, GlueMixin):
    crawler_arn: str = dataclasses.field()

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
        return format_key_value("name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.crawler_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.glue.get_crawler(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
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

        with self.enrich_details(detail_items):
            res = ars.bsm.glue_client.get_tags(ResourceArn=self.arn)
            tags: dict = res.get("Tags", {})
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

        return detail_items


class GlueCrawlerSearcher(res_lib.Searcher[GlueCrawler]):
    pass


glue_crawler_searcher = GlueCrawlerSearcher(
    # list resources
    service="glue",
    method="get_crawlers",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Crawlers"),
    # extract document
    doc_class=GlueCrawler,
    # search
    resource_type=SearcherEnum.glue_crawler,
    fields=res_lib.define_fields(
        fields=[
            res_lib.sayt.StoredField(name="crawler_arn"),
        ],
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

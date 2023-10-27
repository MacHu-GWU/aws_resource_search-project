# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

import aws_arns.api as arns

from .. import res_lib

if T.TYPE_CHECKING:
    from ..ars_v2 import ARS


@dataclasses.dataclass
class GlueDatabase(res_lib.BaseDocument):
    catalog_id: str = dataclasses.field()
    database: str = dataclasses.field()
    description: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    database_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            catalog_id=resource["CatalogId"],
            database=resource["Name"],
            description=resource.get("Description", "No Description"),
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
        return self.database

    @property
    def subtitle(self) -> str:
        return self.description

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.database_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.glue.get_database(database_or_arn=self.arn)


glue_database_searcher = res_lib.Searcher(
    # list resources
    service="glue",
    method="get_databases",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("DatabaseList"),
    # extract document
    doc_class=GlueDatabase,
    # search
    resource_type="glue-database",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="catalog_id"),
        res_lib.sayt.StoredField(name="database"),
        res_lib.sayt.StoredField(name="description"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="database_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class GlueTable(res_lib.BaseDocument):
    catalog_id: str = dataclasses.field()
    database: str = dataclasses.field()
    table: str = dataclasses.field()
    description: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    table_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            catalog_id=resource["CatalogId"],
            database=resource["DatabaseName"],
            table=resource["Name"],
            description=resource.get("Description", "No Description"),
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
        return f"{self.database}.{self.table}"

    @property
    def subtitle(self) -> str:
        return self.description

    @property
    def autocomplete(self) -> str:
        return f"{self.database}@{self.table}"

    @property
    def arn(self) -> str:
        return self.table_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.glue.get_table(table_or_arn=self.arn)


glue_table_searcher = res_lib.Searcher(
    # list resources
    service="glue",
    method="get_tables",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("TableList"),
    # extract document
    doc_class=GlueTable,
    # search
    resource_type="glue-table",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="catalog_id"),
        res_lib.sayt.StoredField(name="database"),
        res_lib.sayt.StoredField(name="table"),
        res_lib.sayt.StoredField(name="description"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="table_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class GlueJob(res_lib.BaseDocument):
    description: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    job_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            description=resource.get("Description", "No Description"),
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
        return self.name

    @property
    def subtitle(self) -> str:
        return self.description

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.job_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.glue.get_job(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        # fmt: off
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

        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        detail_items = [
            Item("description", description),
            Item("role_arn", role_arn, url=aws.iam.get_role(role_arn)),
            Item("glue_version", glue_version),
            Item("worker_type", worker_type),
            Item("number_of_workers", number_of_workers),
            Item("max_concurrent_runs", max_concurrent_runs),
            Item("max_retries", max_retries),
            Item("execution_class", execution_class),
            Item("script_location", script_location, url=aws.s3.get_console_url(uri_liked=script_location)),
        ]
        # fmt: on

        res = ars.bsm.glue_client.get_tags(ResourceArn=self.arn)
        tags: dict = res.get("Tags", {})
        tag_items = res_lib.DetailItem.from_tags(tags)
        return [
            *detail_items,
            *tag_items,
        ]


glue_job_searcher = res_lib.Searcher(
    # list resources
    service="glue",
    method="get_jobs",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Jobs"),
    # extract document
    doc_class=GlueJob,
    # search
    resource_type="glue-job",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="description"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="job_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


_glue_job_run_state_mapper = {
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
    job_name: str = dataclasses.field()
    state: str = dataclasses.field()
    started_on: datetime = dataclasses.field()
    completed_on: datetime = dataclasses.field()
    execution_time: int = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            job_name=resource["JobName"],
            state=resource["JobRunState"],
            started_on=resource.get("StartedOn"),
            completed_on=resource.get("CompletedOn"),
            execution_time=resource.get("ExecutionTime"),
            id=resource["Id"],
            name=resource["Id"],
        )

    @property
    def title(self) -> str:
        return (
            f"{self.id}, <state>: {_glue_job_run_state_mapper[self.state]} {self.state}"
        )

    @property
    def subtitle(self) -> str:
        return (
            f"<job>: {self.job_name}, "
            f"<start>: {str(self.started_on)[:19]}, "
            f"<end>: {str(self.completed_on)[:19]}, "
            f"<elapsed>: {self.execution_time} secs"
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
        # fmt: off
        res = ars.bsm.glue_client.get_job_run(
            JobName=self.job_name,
            RunId=self.id,
        )
        dct = res["JobRun"]

        error_message = dct.get("ErrorMessage", "NA")
        log_group_name = dct.get("LogGroupName", "NA")

        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        detail_items = [
            Item("error_message", error_message),
            Item("output_logs", log_group_name, url=aws.cloudwatch.get_log_stream(stream_name_or_arn=self.id, group_name=f"{log_group_name}/output")),
            Item("error_logs", log_group_name, url=aws.cloudwatch.get_log_stream(stream_name_or_arn=self.id, group_name=f"{log_group_name}/error")),
        ]
        # fmt: on

        args = dct.get("Arguments", {})
        arg_items = [
            res_lib.DetailItem(
                title=f"📝 arg: {k!r} = {v!r}",
                subtitle="📋 'Ctrl A' to copy argument name and value.",
                uid=f"arg {k}",
                variables={"copy": f"{k} = {v}", "url": None},
            )
            for k, v in args.items()
        ]
        if len(arg_items) == 0:
            arg_items = [
                res_lib.DetailItem(
                    title=f"📝 arg: 🔴 No arg found",
                    uid=f"no arg found",
                )
            ]

        return [
            *detail_items,
            *arg_items,
        ]


glue_job_run_searcher = res_lib.Searcher(
    # list resources
    service="glue",
    method="get_job_runs",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 200}},
    result_path=res_lib.ResultPath("JobRuns"),
    # extract document
    doc_class=GlueJobRun,
    # search
    resource_type="glue-jobrun",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="job_name"),
        res_lib.sayt.StoredField(name="state"),
        res_lib.sayt.StoredField(name="started_on"),
        res_lib.sayt.StoredField(name="completed_on"),
        res_lib.sayt.StoredField(name="execution_time"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

glue_crawler_state_icon_mapper = {
    "READY": "🔵",
    "RUNNING": "🟢",
    "STOPPING": "🔴",
}


@dataclasses.dataclass
class GlueCrawler(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
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
        return self.name

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.crawler_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.glue.get_crawler(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        res = ars.bsm.glue_client.get_crawler(Name=self.name)
        dct = res["Crawler"]

        description = dct.get("Description", "NA")
        state = dct.get("State", "NA")
        role_arn = dct["Role"]
        if not role_arn.startswith("arn:"):
            role_arn = arns.res.IamRole.new(
                aws_account_id=ars.bsm.aws_account_id,
                name=role_arn,
            )

        state_icon = glue_crawler_state_icon_mapper[state]
        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        detail_items = [
            Item("description", description),
            Item("state", state, text=f"{state_icon} {state}"),
            Item("role_arn", role_arn, url=aws.iam.get_role(role_arn)),
        ]

        res = ars.bsm.glue_client.get_tags(ResourceArn=self.arn)
        tags: dict = res.get("Tags", {})
        tag_items = res_lib.DetailItem.from_tags(tags)
        return [
            *detail_items,
            *tag_items,
        ]


glue_crawler_searcher = res_lib.Searcher(
    # list resources
    service="glue",
    method="get_crawlers",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Crawlers"),
    # extract document
    doc_class=GlueCrawler,
    # search
    resource_type="glue-crawler",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="crawler_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

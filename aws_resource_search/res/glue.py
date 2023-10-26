# -*- coding: utf-8 -*-

from datetime import datetime
import dataclasses
from .. import res_lib


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
        return f"{self.id}, <state>: {_glue_job_run_state_mapper[self.state]} {self.state}"

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

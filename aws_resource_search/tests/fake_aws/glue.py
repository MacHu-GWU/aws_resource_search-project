# -*- coding: utf-8 -*-

import typing as T

from .utils import guid, envs, rand_env

if T.TYPE_CHECKING:
    from .main import FakeAws


class GlueMixin:
    glue_databases: T.List[str] = list()
    glue_tables: T.List[str] = list()
    glue_jobs: T.List[str] = list()
    glue_job_runs: T.List[str] = list()
    glue_crawlers: T.List[str] = list()

    @classmethod
    def create_glue_database_table(cls: T.Type["FakeAws"]):
        for ith in range(6):
            env = rand_env()
            db_name = f"{env}-{guid}-{ith}-glue-database"
            cls.bsm.glue_client.create_database(
                DatabaseInput=dict(
                    Name=db_name,
                ),
            )
            cls.glue_databases.append(db_name)
            for jth in range(10):
                tb_name = f"{env}-{guid}-{jth}-glue-table"
                cls.bsm.glue_client.create_table(
                    DatabaseName=db_name,
                    TableInput=dict(
                        Name=tb_name,
                    ),
                )
                cls.glue_tables.append(f"{db_name}.{tb_name}")

    @classmethod
    def create_glue_job(cls: T.Type["FakeAws"]):
        for ith in range(10):
            env = rand_env()
            job_name = f"{env}-{guid}-{ith}-glue-job"
            cls.bsm.glue_client.create_job(
                Name=job_name,
                Role="arn:aws:iam::123456789012:role/AWSGlueServiceRoleDefault",
                Command={
                    "Name": "glueetl",
                },
            )
            cls.glue_jobs.append(job_name)

            for _ in range(3):
                res = cls.bsm.glue_client.start_job_run(JobName=job_name)
                job_run_id = res["JobRunId"]
                cls.glue_job_runs.append(job_run_id)

    @classmethod
    def create_glue_crawler(cls: T.Type["FakeAws"]):
        for ith in range(10):
            env = rand_env()
            crawler_name = f"{env}-{guid}-{ith}-glue-crawler"
            cls.bsm.glue_client.create_crawler(
                Name=crawler_name,
                Role="arn:aws:iam::123456789012:role/AWSGlueServiceRoleDefault",
                Targets=dict(S3Targets=[]),
            )
            cls.glue_crawlers.append(crawler_name)

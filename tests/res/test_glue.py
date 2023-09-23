# -*- coding: utf-8 -*-

import moto
from boto_session_manager import BotoSesManager
from aws_resource_search.res.glue import (
    GlueJob,
    GlueDatabase,
    GlueTable,
    GlueSearcher,
)
from aws_resource_search.tests.mock_test import BaseMockTest
from rich import print as rprint


class TestGlueSearcher(BaseMockTest):
    mock_list = [
        moto.mock_glue,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bsm = BotoSesManager()

        job_names = [
            "my-job-dev",
            "my-job-test",
            "my-job-prod",
        ]
        for job_name in job_names:
            cls.bsm.glue_client.create_job(
                Name=job_name,
                Role="arn:aws:iam::123456789012:role/AWSGlueServiceRoleDefault",
                Command={
                    "Name": "glueetl",
                },
            )

        database_names = [
            "my-dev-database",
            "my-test-database",
            "my-prod-database",
        ]

        table_names = [
            "alice_data",
            "bob_data",
            "cathy_data",
        ]

        for database_name in database_names:
            cls.bsm.glue_client.create_database(
                DatabaseInput=dict(
                    Name=database_name,
                )
            )
            for table_name in table_names:
                cls.bsm.glue_client.create_table(
                    DatabaseName=database_name,
                    TableInput=dict(
                        Name=table_name,
                    )
                )

    def test(self):
        sr = GlueSearcher()

        res = sr.list_jobs()
        assert len(res) == 3
        assert isinstance(res[0], GlueJob)

        assert sr.filter_jobs("dev")[0].name == "my-job-dev"
        assert sr.filter_jobs("test")[0].name == "my-job-test"
        assert sr.filter_jobs("prod")[0].name == "my-job-prod"

        res = sr.list_databases()
        assert len(res) == 3
        assert isinstance(res[0], GlueDatabase)

        assert sr.filter_databases("dev")[0].name == "my-dev-database"
        assert sr.filter_databases("test")[0].name == "my-test-database"
        assert sr.filter_databases("prod")[0].name == "my-prod-database"

        database = "my-dev-database"
        res = sr.list_tables(database=database)
        assert len(res) == 3
        assert isinstance(res[0], GlueTable)

        assert sr.filter_tables("alice", database)[0].name == "alice_data"
        assert sr.filter_tables("bob", database)[0].name == "bob_data"
        assert sr.filter_tables("cathy", database)[0].name == "cathy_data"


if __name__ == "__main__":
    from aws_resource_search.tests import run_cov_test

    run_cov_test(__file__, "aws_resource_search.res.glue", preview=False)

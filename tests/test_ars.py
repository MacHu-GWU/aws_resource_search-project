# -*- coding: utf-8 -*-

import moto
import random

from faker import Faker
from rich import print as rprint

import aws_console_url.api as aws_console_url
from aws_resource_search.ars import ARS
from aws_resource_search.tests.fake_aws_res import FakeAws, guid


class TestARS(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        cls.ars = ARS(bsm=cls.bsm)
        if cls.bsm.aws_account_id != "123456789012":
            raise ValueError("This test only works with fake AWS account 123456789012")
        cls.create_cloudformation_stack()
        cls.create_ec2_inst()
        cls.create_glue_database_table_job_and_crawler()
        cls.create_iam()
        cls.create_s3_bucket()

    def test(self):
        ignore = {
            "glue-table",
        }

        ars = self.ars
        # ars.aws_console.glue.get_crawler(name_or_arn=)
        for service_id, resource_type in ars._service_id_and_resource_type_pairs():
            print(f"--- {service_id}-{resource_type} ---")
            if f"{service_id}-{resource_type}" in ignore:
                continue
            rs = ars._get_rs(service_id=service_id, resource_type=resource_type)
            docs = rs.query(guid, refresh_data=True)
            for doc in docs:
                print(doc["id"], doc["name"], doc["console_url"])
                assert guid in doc["name"]

    def test_glue_table(self):
        print(f"--- glue-table ---")
        for db_doc in self.ars.glue_database.query("*")[:1]:
            db_name = db_doc["name"]
            boto_kwargs = {
                "DatabaseName": db_name,
                "PaginationConfig": {
                    "MaxItems": 9999,
                    "PageSize": 1000
                }
            }
            for tb_doc in self.ars.glue_table.query(guid, boto_kwargs=boto_kwargs):
                print(tb_doc["id"], tb_doc["name"], tb_doc["console_url"])


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.ars", preview=False)

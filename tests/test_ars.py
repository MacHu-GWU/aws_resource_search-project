# -*- coding: utf-8 -*-

import moto
import random

from faker import Faker
from rich import print as rprint

import aws_console_url.api as aws_console_url
from aws_resource_search.ars import ARS
from aws_resource_search.logger import logger
from aws_resource_search.tests.fake_aws_res import FakeAws, guid


class TestARS(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        ars = ARS(bsm=cls.bsm)
        # ars.clear_all_cache()
        cls.ars = ars
        if cls.bsm.aws_account_id != "123456789012":
            raise ValueError("This test only works with fake AWS account 123456789012")
        cls.create_cloudformation_stack()
        cls.create_dynamodb_table()
        cls.create_ec2_inst()
        cls.create_glue_database_table_job_and_crawler()
        cls.create_iam()
        cls.create_s3_bucket()

    def _test_all(self):
        ignore = {
            "glue-table",
        }

        ars = self.ars
        # ars.aws_console.dynamodb.get_table(table_or_arn=)
        for service_id, resource_type in ars._service_id_and_resource_type_pairs():
            if f"{service_id}-{resource_type}" in ignore:
                continue
            print(f"--- {service_id}-{resource_type} ---")
            rs = ars._get_rs(service_id=service_id, resource_type=resource_type)
            result = rs.search(
                guid,
                refresh_data=True,
                simple_response=True,
                verbose=False,
            )
            # print(result)
            for doc in result:
                print(doc["id"], doc["name"], doc["console_url"])
                assert guid in doc["name"]

    def _test_glue_table(self):
        print(f"--- glue-table ---")

        rs_glue_db = self.ars._get_rs("glue", "database")
        rs_glue_tb = self.ars._get_rs("glue", "table")
        for db_doc in rs_glue_db.search(
            "*",
            refresh_data=True,
            simple_response=True,
            verbose=True,
        ):
            db_name = db_doc["name"]
            print(f"--- db: {db_name} ---")
            boto_kwargs = {
                "DatabaseName": db_name,
            }
            for tb_doc in rs_glue_tb.search(
                guid,
                boto_kwargs=boto_kwargs,
                refresh_data=True,
                simple_response=True,
                verbose=False,
            ):
                print(tb_doc["id"], tb_doc["name"], tb_doc["console_url"])
                assert guid in tb_doc["name"]

        for db_doc in rs_glue_db.search(
            "*", refresh_data=False, simple_response=True, verbose=True
        ):
            db_name = db_doc["name"]
            print(f"--- db: {db_name} ---")
            boto_kwargs = {
                "DatabaseName": db_name,
            }
            for tb_doc in rs_glue_tb.search(
                guid,
                boto_kwargs=boto_kwargs,
                refresh_data=False,
                simple_response=True,
                verbose=True,
            ):
                print(tb_doc["id"], tb_doc["name"], tb_doc["console_url"])
                assert guid in tb_doc["name"]

    def test(self):
        print("")
        with logger.disabled(
            disable=True,  # no log,
            # disable=False, # show log
        ):
            self._test_all()
            self._test_glue_table()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.ars", preview=False)

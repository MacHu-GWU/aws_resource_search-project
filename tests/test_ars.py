# -*- coding: utf-8 -*-

from rich import print as rprint

from aws_resource_search.ars import ARS
from aws_resource_search.logger import logger
from aws_resource_search.tests.fake_aws_res import FakeAws, guid


class TestARS(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        ars = ARS(bsm=cls.bsm)
        ars.clear_all_cache()

        cls.ars = ars
        if cls.bsm.aws_account_id != "123456789012":
            raise ValueError("This test only works with fake AWS account 123456789012")

        cls.create_cloudformation_stack()
        cls.create_dynamodb_table()
        cls.create_ec2_inst()
        vpc_id_list = cls.create_ec2_vpc()
        cls.vpc_id_list = vpc_id_list
        cls.create_ec2_subnet(vpc_id_list=vpc_id_list)
        cls.create_ec2_securitygroup(vpc_id_list=vpc_id_list)
        cls.create_glue_database_table_job_and_crawler()
        cls.create_iam()
        s3_bucket_list = cls.create_s3_bucket()
        # cls.create_lambda_layers(s3_bucket=s3_bucket_list[0])
        cls.create_lambda_function(s3_bucket=s3_bucket_list[0])

    def _test_all(self):
        """
        这个方法用来测试 list resource 的时候无需任何额外参数的情况, 也就是简单情况.
        """
        ignore = {
            "ec2-subnet",
            "ec2-securitygroup",
            "glue-table",
        }

        ars = self.ars

        # ars.aws_console.sqs.get_queue(name_or_arn_or_url=123)
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

    def _test_ec2_subnet(self):
        print(f"--- ec2-subnet ---")
        rs_ec2_subnet = self.ars._get_rs("ec2", "subnet")
        for doc in rs_ec2_subnet.search(
            guid,
            refresh_data=True,
            simple_response=True,
            verbose=True,
        ):
            print(doc["id"], doc["name"], doc["console_url"])
            assert guid in doc["name"]

        for doc in rs_ec2_subnet.search(
            guid,
            boto_kwargs={
                "Filters": [
                    {
                        "Name": "vpc-id",
                        "Values": [
                            self.vpc_id_list[0],
                        ],
                    },
                ]
            },
            refresh_data=True,
            simple_response=True,
            verbose=True,
        ):
            print(doc["id"], doc["name"], doc["console_url"])
            assert guid in doc["name"]

    def _test_ec2_securitygroup(self):
        print(f"--- ec2-securitygroup ---")
        rs_ec2_sg = self.ars._get_rs("ec2", "securitygroup")
        for doc in rs_ec2_sg.search(
            guid,
            refresh_data=True,
            simple_response=True,
            verbose=True,
        ):
            print(doc["id"], doc["name"], doc["console_url"])
            assert guid in doc["name"]

        for doc in rs_ec2_sg.search(
            guid,
            boto_kwargs={
                "Filters": [
                    {
                        "Name": "vpc-id",
                        "Values": [
                            self.vpc_id_list[0],
                        ],
                    },
                ]
            },
            refresh_data=True,
            simple_response=True,
            verbose=True,
        ):
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
            self._test_ec2_subnet()
            self._test_ec2_securitygroup()
            self._test_glue_table()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.ars", preview=False)

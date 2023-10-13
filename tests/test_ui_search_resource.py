# -*- coding: utf-8 -*-

import typing as T
from rich import print as rprint

import afwf_shell.api as afwf_shell
from aws_resource_search.tests.fake_aws_res import FakeAws, guid


class TestUI(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        from aws_resource_search.ui import handler, ars

        cls.ui = afwf_shell.UI(handler=handler)
        cls.ars = ars
        cls.service_id_and_resource_type_pairs = (
            ars._service_id_and_resource_type_pairs()
        )

        ars.clear_all_cache()

        if cls.bsm.aws_account_id != "123456789012":
            raise ValueError("This test only works with fake AWS account 123456789012")

        # cls.create_cloudformation_stack()
        # cls.create_dynamodb_table()
        # cls.create_ec2_inst()
        # vpc_id_list = cls.create_ec2_vpc()
        # cls.vpc_id_list = vpc_id_list
        # cls.create_ec2_subnet(vpc_id_list=vpc_id_list)
        # cls.create_ec2_securitygroup(vpc_id_list=vpc_id_list)
        # cls.create_glue_database_table_job_and_crawler()
        # cls.create_iam()
        cls.create_s3_bucket()

    def _test(self):
        from aws_resource_search.ui import handler

        items = handler(query="s3-bucket: ", ui=self.ui)
        for item in items:
            assert item.uid.endswith("bucket")

        items = handler(query=f"s3-bucket: tst", ui=self.ui)
        for item in items:
            assert "tst" in item.uid

        rprint(items[:5])

    def test(self):
        self._test()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.ui", preview=False)

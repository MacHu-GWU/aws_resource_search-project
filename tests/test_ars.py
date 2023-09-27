# -*- coding: utf-8 -*-

import moto
import random

from faker import Faker
from rich import print as rprint

import aws_console_url.api as aws_console_url
from aws_resource_search.ars import ARS
from aws_resource_search.tests.fake_aws_res import FakeAws, guid


class TestARS(FakeAws):
    def test(self):
        # self.create_ec2_inst()
        # self.create_s3_bucket()
        self.create_cloudformation_stack()

        ars = ARS(bsm=self.bsm)

        for service_id, resource_type in ars._service_id_and_resource_type_pairs():
            print(f"--- {service_id}-{resource_type} ---")
            rs = ars._get_rs(service_id=service_id, resource_type=resource_type)
            docs = rs.query(guid, refresh_data=True)
            # print(docs)
            for doc in docs:
                print(doc["name"], doc["console_url"])
                assert guid in doc["name"]

        # rs = ars._get_rs(service_id="cloudformation", resource_type="stack")
        # rs = ars._get_rs(service_id="ec2", resource_type="instance")

        # print(rs.cache_key)
        # docs = rs.query("*", refresh_data=True)
        # rprint(docs)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.ars", preview=False)

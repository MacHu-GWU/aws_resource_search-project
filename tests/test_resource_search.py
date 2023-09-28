# -*- coding: utf-8 -*-

import moto
import random

from faker import Faker
from rich import print as rprint

import aws_console_url.api as aws_console_url
from aws_resource_search.constants import _RES, _OUT, RAW_DATA
from aws_resource_search.logger import logger
from aws_resource_search.data.request import parse_req_json_node
from aws_resource_search.data.output import parse_out_json_node
from aws_resource_search.data.document import parse_doc_json_node
from aws_resource_search.data.url import parse_url_json_node

from aws_resource_search.resource_searcher import ResourceSearcher
from aws_resource_search.tests.mock_test import BaseMockTest

fake = Faker()


class TestResourceSearcher(BaseMockTest):
    mock_list = [moto.mock_ec2, moto.mock_glue]

    def _create_test_ec2(self):
        image_id = self.bsm.ec2_client.describe_images()["Images"][0]["ImageId"]
        words = [
            "alice",
            "bob",
            "cathy",
            "david",
            "edward",
            "frank",
            "george",
            "hunter",
            "ivan",
            "john",
            "kevin",
            "lincoln",
            "maria",
            "nathan",
        ]
        for _ in range(100):
            kwargs = dict(
                MinCount=1,
                MaxCount=1,
                ImageId=image_id,
            )
            if random.randint(1, 100) <= 70:
                kwargs["TagSpecifications"] = [
                    dict(
                        ResourceType="instance",
                        Tags=[
                            dict(
                                Key="Name",
                                Value=" ".join(
                                    random.sample(words, random.randint(2, 3))
                                ),
                            ),
                        ],
                    )
                ]
            self.bsm.ec2_client.run_instances(**kwargs)

    def _create_test_glue(self):
        db_name_1 = f"dev_db"
        db_name_2 = f"prd_db"
        for db_name in [db_name_1, db_name_2]:
            self.bsm.glue_client.create_database(
                DatabaseInput=dict(Name=db_name),
            )

        for ith in range(1, 1 + 2):
            tb_name = f"dev_table_{ith}"
            self.bsm.glue_client.create_table(
                DatabaseName=db_name_1,
                TableInput=dict(
                    Name=tb_name,
                ),
            )

        for ith in range(1, 1 + 3):
            tb_name = f"prd_table_{ith}"
            self.bsm.glue_client.create_table(
                DatabaseName=db_name_2,
                TableInput=dict(
                    Name=tb_name,
                ),
            )

    def _test_ec2(self):
        self._create_test_ec2()

        rs = ResourceSearcher(
            bsm=self.bsm,
            aws_console=aws_console_url.AWSConsole(
                aws_account_id=self.bsm.aws_account_id,
                aws_region=self.bsm.aws_region,
                bsm=self.bsm,
            ),
            service_id="ec2",
            resource_type="instance",
            request=parse_req_json_node(
                {
                    "client": "ec2",
                    "method": "describe_instances",
                    "kwargs": {"PaginationConfig": {"MaxItems": 1000, "PageSize": 100}},
                    "is_paginator": True,
                    "result_path": "$Reservations[].Instances[] || `[]`",
                }
            ),
            output=parse_out_json_node(
                {
                    "arn": {
                        "type": "str",
                        "token": {
                            "type": "sub",
                            "kwargs": {
                                "template": "arn:aws:ec2:{aws_region}:{aws_account_id}:instance/{instance_id}",
                                "params": {
                                    "instance_id": "$_res.InstanceId",
                                    "aws_region": "$_ctx.AWS_REGION",
                                    "aws_account_id": "$_ctx.AWS_ACCOUNT_ID",
                                },
                            },
                        },
                    },
                    "title": {
                        "type": "str",
                        "token": "$_res.Tags[?Key=='Name'].Value | [0] || 'No instance name'",
                    },
                    "subtitle": {
                        "type": "str",
                        "token": {
                            "type": "sub",
                            "kwargs": {
                                "template": "{state} | {inst_id} | {inst_type}",
                                "params": {
                                    "state": "$_res.State.Name",
                                    "inst_id": "$_res.InstanceId",
                                    "inst_type": "$_res.InstanceType",
                                },
                            },
                        },
                    },
                }
            ),
            document=parse_doc_json_node(
                {
                    "id": {
                        "type": "Id",
                        "token": "$_res.InstanceId",
                        "kwargs": {
                            "stored": True,
                            "field_boost": 10,
                        },
                    },
                    "instance_id_ngram": {
                        "type": "Ngram",
                        "token": "$_res.InstanceId",
                        "kwargs": {"stored": False},
                    },
                    "name": {
                        "type": "NgramWords",
                        "token": "$_res.Tags[?Key=='Name'].Value | [0] || 'No instance name'",
                        "kwargs": {"stored": True},
                    },
                }
            ),
            url=parse_url_json_node(
                {
                    "service_id": "ec2",
                    "method": "get_instance",
                    "kwargs": {"instance_id_or_arn": "$raw_data._res.InstanceId"},
                }
            ),
            cache_expire=1,
        )
        result = rs.search("john", refresh_data=True, verbose=True)
        for hit in result["hits"]:
            doc = hit["_source"]
            ec2_name = doc[RAW_DATA][_RES]["Tags"][0]["Value"]
            assert "john" in ec2_name
            arn = doc[RAW_DATA][_OUT]["arn"]
            assert arn.startswith("arn:")

    def _test_glue(self):
        self._create_test_glue()

        rs = ResourceSearcher(
            bsm=self.bsm,
            aws_console=aws_console_url.AWSConsole(
                aws_account_id=self.bsm.aws_account_id,
                aws_region=self.bsm.aws_region,
                bsm=self.bsm,
            ),
            service_id="glue",
            resource_type="table",
            request=parse_req_json_node(
                {
                    "client": "glue",
                    "method": "get_tables",
                    "kwargs": {"PaginationConfig": {"MaxItems": 1000, "PageSize": 100}},
                    "cache_key": ["$DatabaseName"],
                    "is_paginator": True,
                    "result_path": "$TableList || `[]`",
                }
            ),
            output=parse_out_json_node({}),
            document=parse_doc_json_node(
                {
                    "name": {
                        "type": "NgramWords",
                        "token": {
                            "type": "sub",
                            "kwargs": {
                                "template": "{database}.{table}",
                                "params": {
                                    "database": "$_res.DatabaseName",
                                    "table": "$_res.Name",
                                },
                            },
                        },
                        "kwargs": {"stored": True},
                    },
                }
            ),
            url=parse_url_json_node(
                {
                    "service_id": "glue",
                    "method": "get_table",
                    "kwargs": {
                        "table_or_arn": "$raw_data._res.Name",
                        "database": "$raw_data._res.DatabaseName",
                        "catalog_id": "123456789012",
                    },
                }
            ),
            cache_expire=1,
        )

        db_name = "dev_db"
        result = rs.search(
            "dev",
            boto_kwargs={"DatabaseName": db_name},
            refresh_data=True,
            verbose=True,
        )
        # rprint(result)
        assert result["size"] == 2
        assert result["cache"] == False
        for hit in result["hits"]:
            doc = hit["_source"]
            # print(doc["name"])
            assert doc["name"].startswith(f"{db_name}.")

        result = rs.search(
            "dev",
            boto_kwargs={"DatabaseName": db_name},
            refresh_data=False,
            verbose=True,
        )
        # rprint(result)
        assert result["size"] == 2
        assert result["cache"] == True
        for hit in result["hits"]:
            doc = hit["_source"]
            # print(doc["name"])
            assert doc["name"].startswith(f"{db_name}.")

        db_name = "prd_db"
        result = rs.search(
            "prd",
            boto_kwargs={"DatabaseName": db_name},
            refresh_data=True,
            verbose=True,
        )
        # rprint(result)
        assert result["size"] == 3
        assert result["cache"] == False
        for hit in result["hits"]:
            doc = hit["_source"]
            # print(doc["name"])
            assert doc["name"].startswith(f"{db_name}.")

        result = rs.search(
            "prd",
            boto_kwargs={"DatabaseName": db_name},
            refresh_data=False,
            verbose=True,
        )
        # rprint(result)
        assert result["size"] == 3
        assert result["cache"] == True
        for hit in result["hits"]:
            doc = hit["_source"]
            # print(doc["name"])
            assert doc["name"].startswith(f"{db_name}.")

    def test(self):
        print("")
        with logger.disabled(
            disable=True,  # no log,
            # disable=False, # show log
        ):
            self._test_ec2()
            self._test_glue()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.resource_searcher", preview=False)

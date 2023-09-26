# -*- coding: utf-8 -*-

import moto
import random

from faker import Faker
from rich import print as rprint

import aws_console_url.api as aws_console_url
from aws_resource_search.data.request import Request
from aws_resource_search.data.search import Search
from aws_resource_search.resource_searcher import ResourceSearcher
from aws_resource_search.tests.mock_test import BaseMockTest


fake = Faker()


class TestResourceSearcher(BaseMockTest):
    mock_list = [
        moto.mock_ec2,
    ]

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

    def test(self):
        self._create_test_ec2()

        request_data = {
            "client": "ec2",
            "method": "describe_instances",
            "kwargs": {"PaginationConfig": {"MaxItems": 1000, "PageSize": 100}},
            "is_paginator": True,
            "items_path": "$Reservations[].Instances[] || `[]`",
            "result": {
                "arn": {
                    "type": "str",
                    "value": {
                        "type": "sub",
                        "kwargs": {
                            "template": "arn:aws:ec2:{AWS_REGION}:{AWS_ACCOUNT_ID}:instance/{instance_id}",
                            "params": {"instance_id": "$InstanceId"},
                        },
                    },
                },
                "title": {
                    "type": "str",
                    "value": "$Tags[?Key=='Name'].Value | [0] || 'No instance name'",
                },
                "subtitle": {
                    "type": "str",
                    "value": {
                        "type": "sub",
                        "kwargs": {
                            "template": "{state} | {inst_id} | {inst_type}",
                            "params": {
                                "state": "$State.Name",
                                "inst_id": "$InstanceId",
                                "inst_type": "$InstanceType",
                            },
                        },
                    },
                },
            },
        }
        request = Request.from_dict(request_data)
        search_data = {
            "fields": [
                {
                    "name": "instance_id",
                    "type": "Id",
                    "value": "$_item.InstanceId",
                    "kwargs": {
                        "field_boost": 10,
                    },
                },
                {
                    "name": "instance_id_ngram",
                    "type": "Ngram",
                    "value": "$_item.InstanceId",
                },
                {
                    "name": "name",
                    "type": "NgramWords",
                    "value": "$_item.Tags[?Key=='Name'].Value | [0] || 'No instance name'",
                },
            ]
        }
        search = Search.from_dict(search_data)

        rs = ResourceSearcher(
            bsm=self.bsm,
            aws_console=aws_console_url.AWSConsole(
                aws_account_id=self.bsm.aws_account_id,
                aws_region=self.bsm.aws_region,
                bsm=self.bsm,
            ),
            service_id="ec2",
            resource_type="instance",
            request=request,
            search=search,
            cache_expire=1,
        )
        docs = rs.query("john")
        for doc in docs:
            ec2_name = doc["raw_item"]["Tags"][0]["Value"]
            assert "john" in ec2_name


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.resource_searcher", preview=False)

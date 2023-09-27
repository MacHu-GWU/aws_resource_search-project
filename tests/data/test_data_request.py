# -*- coding: utf-8 -*-

import moto
from aws_resource_search.constants import TokenTypeEnum, _ITEM, _RESULT
from aws_resource_search.data.request import Attribute, Request
from aws_resource_search.tests.mock_test import BaseMockTest
from rich import print as rprint


class TestAttribute:
    def test(self):
        attr = Attribute(type="str", value="hello")
        assert attr.to_dict() == {"type": "str", "value": "hello"}
        assert Attribute.from_dict({"type": "str", "value": "hello"}) == attr


class TestRequest:
    def test(self):
        req = Request(
            client="ec2",
            method="describe_instances",
            is_paginator=True,
            items_path="$Reservations[].Instances[] || `[]`",
            result={
                "arn": Attribute.from_dict({"type": "str", "value": "ec2_arn"}),
            },
        )
        assert req.to_dict() == {
            "client": "ec2",
            "method": "describe_instances",
            "kwargs": {},
            "is_paginator": True,
            "items_path": "$Reservations[].Instances[] || `[]`",
            "result": {"arn": {"type": "str", "value": "ec2_arn"}},
        }
        assert (
            Request.from_dict(
                {
                    "client": "ec2",
                    "method": "describe_instances",
                    "kwargs": {},
                    "is_paginator": True,
                    "items_path": "$Reservations[].Instances[] || `[]`",
                    "result": {"arn": {"type": "str", "value": "ec2_arn"}},
                }
            )
            == req
        )


class TestS3AndIamRequest(BaseMockTest):
    mock_list = [
        moto.mock_s3,
        moto.mock_iam,
    ]

    def _create_test_buckets(self):
        self.bucket_names = [
            "company-data",
            "enterprise-data",
        ]
        for bucket_name in self.bucket_names:
            self.bsm.s3_client.create_bucket(Bucket=bucket_name)

    def _create_test_iam_groups(self):
        self.iam_group_names = [
            "admin_group",
            "developer_group",
        ]
        for iam_group_name in self.iam_group_names:
            self.bsm.iam_client.create_group(GroupName=iam_group_name)

    def test_no_paginator(self):
        request = Request(
            client="s3",
            method="list_buckets",
            is_paginator=False,
            items_path="$Buckets",
            result={
                "name": Attribute.from_dict({"type": "str", "value": "$Name"}),
                "message": Attribute.from_dict({"type": "str", "value": "hello"}),
            },
        )
        assert len(request.invoke(self.bsm).all()) == 0

        self._create_test_buckets()

        res = request.invoke(self.bsm).all()
        assert res[0][_RESULT]["name"] == "company-data"
        assert res[0][_RESULT]["message"] == "hello"
        assert res[1][_RESULT]["name"] == "enterprise-data"
        assert res[1][_RESULT]["message"] == "hello"
        assert set(res[1]) == {_ITEM, _RESULT}

        # ----------------------------------------------------------------------
        request.result = None
        item = request.invoke(self.bsm).one()["_item"]
        assert set(item) == {"Name", "CreationDate"}

        # ----------------------------------------------------------------------
        request.result = {
            "Arn": Attribute.from_dict(
                {
                    "type": "str",
                    "value": {
                        "type": TokenTypeEnum.sub,
                        "kwargs": {
                            "template": "arn:aws:s3:{AWS_REGION}:{AWS_ACCOUNT_ID}:bucket/{bucket}",
                            "params": {"bucket": "$Name"},
                        },
                    },
                }
            ),
        }

        res = request.invoke(self.bsm).all()
        assert (
            res[0][_RESULT]["Arn"]
            == "arn:aws:s3:us-east-1:123456789012:bucket/company-data"
        )
        assert (
            res[1][_RESULT]["Arn"]
            == "arn:aws:s3:us-east-1:123456789012:bucket/enterprise-data"
        )

    def test_paginator(self):
        request = Request(
            client="iam",
            method="list_groups",
            kwargs=dict(
                PaginationConfig=dict(
                    MaxItems=9999,
                    PageSize=1000,
                )
            ),
            is_paginator=True,
            items_path="$Groups",
        )
        assert len(request.invoke(self.bsm).all()) == 0

        self._create_test_iam_groups()
        res = request.invoke(self.bsm).all()
        assert len(res) == 2
        assert [item[_ITEM]["GroupName"] for item in res] == self.iam_group_names


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.data.request", preview=False)

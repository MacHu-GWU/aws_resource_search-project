# -*- coding: utf-8 -*-

import moto
from aws_resource_search.data.request import Request
from aws_resource_search.tests.mock_test import BaseMockTest
from rich import print as rprint


class Test(BaseMockTest):
    mock_list = [
        moto.mock_s3,
        moto.mock_iam,
    ]

    def _test_Request_seder(self):
        req = Request(
            client="ec2",
            method="describe_instances",
            is_paginator=True,
            result_path="$Reservations[].Instances[] || `[]`",
        )
        assert req.to_dict() == {
            "client": "ec2",
            "method": "describe_instances",
            "kwargs": {},
            "cache_key": [],
            "is_paginator": True,
            "result_path": "$Reservations[].Instances[] || `[]`",
        }
        assert (
            Request.from_dict(
                {
                    "client": "ec2",
                    "method": "describe_instances",
                    "kwargs": {},
                    "cache_key": [],
                    "is_paginator": True,
                    "result_path": "$Reservations[].Instances[] || `[]`",
                }
            )
            == req
        )

    def _test_Request_merge_boto_kwargs(self):
        request = Request(
            client="ec2",
            method="describe_instances",
            is_paginator=True,
            kwargs=dict(
                PaginationConfig=dict(
                    MaxItems=9999,
                    PageSize=1000,
                )
            ),
            result_path="",
        )
        assert request._merge_boto_kwargs({"InstanceIds": []}) == {
            "InstanceIds": [],
            "PaginationConfig": {
                "MaxItems": 9999,
                "PageSize": 1000,
            },
        }
        assert request._merge_boto_kwargs({"PaginationConfig": {}}) == {
            "PaginationConfig": {},
        }

        request.client = "glue"
        request.method = "get_databases"
        request.kwargs = dict(CatalogId="$AWS_ACCOUNT_ID")
        assert request._merge_boto_kwargs(
            None, context={"AWS_ACCOUNT_ID": "123456789012"}
        ) == {
            "CatalogId": "123456789012",
        }

    def _test_Request_get_additional_cache_key(self):
        request = Request(
            client="glue",
            method="get_databases",
            is_paginator=True,
            cache_key=["$CatalogId"],
            result_path="",
        )
        assert request._get_additional_cache_key({"CatalogId": "123456789012"}) == [
            "123456789012"
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

    def _test_s3_not_paginator(self):
        request = Request(
            client="s3",
            method="list_buckets",
            is_paginator=False,
            result_path="$Buckets",
        )
        assert len(request.send(self.bsm).all()) == 0

        self._create_test_buckets()

        res = request.send(self.bsm).all()
        assert res[0]["Name"] == "company-data"
        assert res[1]["Name"] == "enterprise-data"

    def _test_iam_is_paginator(self):
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
            result_path="$Groups",
        )
        assert len(request.send(self.bsm).all()) == 0

        self._create_test_iam_groups()
        res = request.send(self.bsm).all()
        assert len(res) == 2
        assert res[0]["GroupName"] == "admin_group"
        assert res[1]["GroupName"] == "developer_group"

    def test(self):
        self._test_Request_seder()
        self._test_Request_merge_boto_kwargs()
        self._test_Request_get_additional_cache_key()
        self._test_s3_not_paginator()
        self._test_iam_is_paginator()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.data.request", preview=False)

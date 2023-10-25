# -*- coding: utf-8 -*-

import moto
from aws_resource_search.res_lib import (
    ResultPath,
    list_resources,
)
from aws_resource_search.tests.mock_test import BaseMockTest
from rich import print as rprint


class Test(BaseMockTest):
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

    def _test_list_resources_1_s3_not_paginator(self):
        def func():
            return list_resources(
                bsm=self.bsm,
                service="s3",
                method="list_buckets",
                is_paginator=False,
                boto_kwargs=None,
                result_path=ResultPath(path="Buckets"),
            ).all()

        assert len(func()) == 0
        self._create_test_buckets()
        res = func()
        assert len(res) == 2
        assert res[0]["Name"] == "company-data"
        assert res[1]["Name"] == "enterprise-data"

    def _test_list_resources_2_iam_is_paginator(self):
        def func():
            return list_resources(
                bsm=self.bsm,
                service="iam",
                method="list_groups",
                is_paginator=True,
                boto_kwargs=dict(
                    PaginationConfig=dict(
                        MaxItems=9999,
                        PageSize=1000,
                    )
                ),
                result_path=ResultPath(path="Groups"),
            ).all()

        assert len(func()) == 0
        self._create_test_iam_groups()
        res = func()
        assert len(res) == 2
        assert res[0]["GroupName"] == "admin_group"
        assert res[1]["GroupName"] == "developer_group"

    def _test_list_resources(self):
        self._test_list_resources_1_s3_not_paginator()
        self._test_list_resources_2_iam_is_paginator()

    def test(self):
        self._test_list_resources()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.res_lib", preview=False)

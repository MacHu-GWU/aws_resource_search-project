# -*- coding: utf-8 -*-

from aws_console_url.api import AWSConsole
from aws_resource_search.tests.mock_test import BaseMockTest
from aws_resource_search.data.url import Url

from rich import print as rprint


class Test(BaseMockTest):
    def _test_Url(self):
        aws_console = AWSConsole(
            aws_account_id=self.bsm.aws_account_id,
            aws_region=self.bsm.aws_region,
            bsm=self.bsm,
        )

        url = Url(service_id="s3", method="get_console_url", kwargs={"bucket": "$name"})
        console_url = url.get(
            {
                "id": "my-bucket",
                "name": "my-bucket",
                "raw_data": {"_res": {}, "_out": {}},
            },
            aws_console,
        )
        assert (
            console_url
            == "https://us-east-1.console.aws.amazon.com/s3/buckets/my-bucket?region=us-east-1&tab=objects"
        )

    def test(self):
        self._test_Url()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.data.url", preview=False)

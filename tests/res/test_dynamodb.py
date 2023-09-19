# -*- coding: utf-8 -*-

import moto
from boto_session_manager import BotoSesManager
from aws_resource_search.res.dynamodb import TableSearcher
from aws_resource_search.tests.mock_test import BaseMockTest


class TestDynamodbSearcher(BaseMockTest):
    mock_list = [
        moto.mock_dynamodb,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bsm = BotoSesManager()

        table_names = [
            "virtual-machines",
            "containers",
        ]
        for table_name in table_names:
            cls.bsm.dynamodb_client.create_table(
                TableName=table_name,
                AttributeDefinitions=[
                    dict(
                        AttributeName="pk",
                        AttributeType="S",
                    ),
                ],
                KeySchema=[
                    dict(
                        AttributeName="pk",
                        KeyType="HASH",
                    )
                ],
                BillingMode="PAY_PER_REQUEST",
            )

    def test(self):
        sr = TableSearcher()
        assert len(sr.list_tables()) == 2
        assert len(sr.list_tables()) == 2

        assert "virtual-machines" in sr.filter_tables("virtual-machines")[0].name
        assert "containers" in sr.filter_tables("containers")[0].name


if __name__ == "__main__":
    from aws_resource_search.tests import run_cov_test

    run_cov_test(__file__, "aws_resource_search.res.dynamodb", preview=False)

# -*- coding: utf-8 -*-

import typing as T
import random

from .utils import guid, envs, rand_env

if T.TYPE_CHECKING:
    from .main import FakeAws


class DynamodbMixin:
    dynamodb_tables: T.List[str] = list()

    @classmethod
    def create_dynamodb_tables(cls: T.Type["FakeAws"]):
        for ith in range(1, 1 + 10):
            env = rand_env()
            table = f"{env}-{guid}-{ith}-dynamodb-table"
            kwargs = dict(
                TableName=table,
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
            # 70% table only has hash key, 30% table also has sort key
            if random.randint(1, 100) <= 30:
                kwargs["AttributeDefinitions"].append(
                    dict(
                        AttributeName="sk",
                        AttributeType="S",
                    )
                )
                kwargs["KeySchema"].append(
                    dict(
                        AttributeName="sk",
                        KeyType="RANGE",
                    )
                )
            cls.bsm.dynamodb_client.create_table(**kwargs)
            cls.dynamodb_tables.append(table)
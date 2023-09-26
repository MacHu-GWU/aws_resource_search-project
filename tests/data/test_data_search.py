# -*- coding: utf-8 -*-

from aws_resource_search.data.search import Search, Field, FieldTypeEnum
from rich import print as rprint


class TestSearch:
    def test(self):
        search = Search(
            fields=[
                Field(
                    name="instance_id",
                    type=FieldTypeEnum.Id.value,
                    value="$InstanceId",
                    kwargs={
                        "field_boost": 10,
                    },
                )
            ]
        )
        assert search.to_dict() == {
            "fields": [
                {
                    "name": "instance_id",
                    "type": "Id",
                    "value": "$InstanceId",
                    "kwargs": {"field_boost": 10},
                }
            ]
        }
        assert (
            Search.from_dict(
                {
                    "fields": [
                        {
                            "name": "instance_id",
                            "type": "Id",
                            "value": "$InstanceId",
                            "kwargs": {"field_boost": 10},
                        }
                    ]
                }
            )
            == search
        )


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.data.search", preview=False)

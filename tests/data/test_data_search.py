# -*- coding: utf-8 -*-

from aws_console_url.api import AWSConsole
from aws_resource_search.constants import _ITEM, _RESULT, RAW_ITEM, RAW_RESULT
from aws_resource_search.data.search import Search, Field, FieldTypeEnum, UrlGetter
from rich import print as rprint


class TestSearch:
    def test(self):
        search = Search(
            fields=[
                Field(
                    name="instance_id",
                    type=FieldTypeEnum.Id.value,
                    value="$_item.InstanceId",
                    kwargs={
                        "field_boost": 10,
                    },
                )
            ],
            url_getter=UrlGetter(
                service_id="ec2",
                method="get_instance",
                kwargs={"instance_id_or_arn": "$raw_item.InstanceId"},
            ),
        )
        assert search.to_dict() == {
            "fields": [
                {
                    "name": "instance_id",
                    "type": "Id",
                    "value": "$_item.InstanceId",
                    "kwargs": {"field_boost": 10},
                },
                {
                    "name": "raw_item",
                    "type": "Stored",
                    "value": "$_item",
                    "kwargs": {},
                },
                {
                    "name": "raw_result",
                    "type": "Stored",
                    "value": "$_result",
                    "kwargs": {},
                },
            ],
            "url_getter": {
                "service_id": "ec2",
                "method": "get_instance",
                "kwargs": {"instance_id_or_arn": "$raw_item.InstanceId"},
            },
        }
        search1 = Search.from_dict(
            {
                "fields": [
                    {
                        "name": "instance_id",
                        "type": "Id",
                        "value": "$_item.InstanceId",
                        "kwargs": {"field_boost": 10},
                    }
                ],
                "url_getter": {
                    "service_id": "ec2",
                    "method": "get_instance",
                    "kwargs": {"instance_id_or_arn": "$raw_item.InstanceId"},
                },
            }
        )
        assert search1 == search

        item = {
            _ITEM: {
                "InstanceId": "i-1234567890abcdef0",
            },
            _RESULT: {},
        }
        doc = search._item_to_doc(item)
        assert doc == {
            "instance_id": "i-1234567890abcdef0",
            RAW_ITEM: {"InstanceId": "i-1234567890abcdef0"},
            RAW_RESULT: {},
        }
        aws_console = AWSConsole(
            aws_account_id="123456789012", aws_region="us-east-1", bsm=None
        )
        url = search._doc_to_url(doc, aws_console)
        assert (
            url
            == "https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#InstanceDetails:instanceId=i-1234567890abcdef0"
        )


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.data.search", preview=False)

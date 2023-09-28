# -*- coding: utf-8 -*-

from aws_resource_search.constants import TokenTypeEnum, _RES, _CTX, _OUT
from aws_resource_search.data.output import (
    Attribute,
    parse_out_json_node,
    extract_output,
)

from rich import print as rprint


class Test:
    def _test_Attribute(self):
        attr = Attribute(type="str", token="hello")
        assert attr.to_dict() == {"type": "str", "token": "hello"}
        assert Attribute.from_dict({"type": "str", "token": "hello"}) == attr

        attr = Attribute(type="str", token="$Name")
        assert attr.evaluate({"Name": "alice"}) == "alice"

    def _test_extract_output(self):
        data = extract_output(
            output=parse_out_json_node(
                {
                    "arn": {
                        "type": "str",
                        "token": {
                            "type": TokenTypeEnum.sub,
                            "kwargs": {
                                "template": "arn:aws:s3:{aws_region}:{aws_account_id}:bucket/{bucket}",
                                "params": {
                                    "bucket": f"${_RES}.Name",
                                    "aws_region": f"${_CTX}.AWS_REGION",
                                    "aws_account_id": f"${_CTX}.AWS_ACCOUNT_ID",
                                },
                            },
                        },
                    },
                }
            ),
            resource={
                "Name": "my-bucket",
            },
            context={"AWS_ACCOUNT_ID": "123456789012", "AWS_REGION": "us-east-1"},
        )
        assert data[_OUT] == {
            "arn": "arn:aws:s3:us-east-1:123456789012:bucket/my-bucket"
        }

    def test(self):
        self._test_Attribute()
        self._test_extract_output()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.data.output", preview=False)

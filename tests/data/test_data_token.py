# -*- coding: utf-8 -*-

from aws_resource_search.data.token import (
    TokenTypeEnum,
    RawToken,
    JmespathToken,
    SubToken,
    evaluate_token,
)
from rich import print as rprint

data = {
    "firstname": "John",
    "lastname": "Doe",
}


class TestEvaluateToken:
    def _test_1(self):
        # implicit raw token
        assert evaluate_token("hello", data) == "hello"
        # implicit jmespath token
        assert evaluate_token("$firstname", data) == "John"
        # explicit raw token
        assert (
            evaluate_token(
                {
                    "type": TokenTypeEnum.raw,
                    "kwargs": {"value": "hello"},
                },
                data,
            )
            == "hello"
        )
        assert evaluate_token(
            {
                "type": TokenTypeEnum.raw,
                "kwargs": {"value": {"type": TokenTypeEnum.raw}},
            },
            data,
        ) == {"type": TokenTypeEnum.raw}
        # explicit jmespath token
        assert (
            evaluate_token(
                {
                    "type": TokenTypeEnum.jmespath,
                    "kwargs": {"path": "$firstname"},
                },
                data,
            )
            == "John"
        )
        # string template token
        assert (
            evaluate_token(
                {
                    "type": TokenTypeEnum.sub,
                    "kwargs": {
                        "template": "Hello {FIRSTNAME} {LASTNAME}! Today is {DATE}, it's my {AGE} years birthday!",
                        "params": {
                            "FIRSTNAME": "$firstname",
                            # params can be any token
                            "LASTNAME": {
                                "type": TokenTypeEnum.jmespath,
                                "kwargs": {"path": "$lastname"},
                            },
                            "AGE": 18,
                        },
                    },
                },
                data,
                context={"DATE": "2021-01-01"},
            )
            == "Hello John Doe! Today is 2021-01-01, it's my 18 years birthday!"
        )

        # string template token
        assert (
            evaluate_token(
                {
                    "type": TokenTypeEnum.join,
                    "kwargs": {
                        "sep": ", ",
                        "array": [
                            "$lastname",
                            {
                                "type": TokenTypeEnum.jmespath,
                                "kwargs": {"path": "$firstname"},
                            },
                        ],
                    },
                },
                data,
            )
            == "Doe, John"
        )

    def test(self):
        self._test_1()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.data.token", preview=False)

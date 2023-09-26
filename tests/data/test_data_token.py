# -*- coding: utf-8 -*-

from aws_resource_search.data.token import (
    TokenTypeEnum,
    RawToken,
    JmespathToken,
    SubToken,
    JoinToken,
    evaluate_token,
)
from rich import print as rprint

data = {
    "firstname": "John",
    "lastname": "Doe",
}


class TestRawToken:
    def test(self):
        token = RawToken(value="hello")
        assert token.evaluate(None, None) == "hello"
        assert token.to_dict() == {"value": "hello"}
        assert RawToken.from_dict({"value": "hello"}) == token


class TestJmespathToken:
    def test(self):
        token = JmespathToken(path="$name")
        assert token.evaluate({"name": "John"}) == "John"
        assert token.to_dict() == {"path": "$name"}
        assert JmespathToken.from_dict({"path": "$name"}) == token


class TestSubToken:
    def test(self):
        token = SubToken(template="hello {name}", params={"name": "$name"})
        assert token.evaluate({"name": "John"}) == "hello John"
        assert token.to_dict() == {
            "template": "hello {name}",
            "params": {"name": "$name"},
        }
        assert (
            SubToken.from_dict(
                {
                    "template": "hello {name}",
                    "params": {"name": "$name"},
                }
            )
            == token
        )


class TestJoinToken:
    def test(self):
        token = JoinToken(
            sep=", ",
            array=[
                "$lastname",
                {"type": "jmespath", "kwargs": {"path": "$firstname"}},
            ],
        )
        assert token.evaluate({"firstname": "John", "lastname": "Doe"}) == "Doe, John"
        assert token.to_dict() == {
            "sep": ", ",
            "array": [
                "$lastname",
                {"type": "jmespath", "kwargs": {"path": "$firstname"}},
            ],
        }
        assert (
            JoinToken.from_dict(
                {
                    "sep": ", ",
                    "array": [
                        "$lastname",
                        {"type": "jmespath", "kwargs": {"path": "$firstname"}},
                    ],
                }
            )
            == token
        )


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

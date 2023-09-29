# -*- coding: utf-8 -*-

from aws_resource_search.data.token import (
    TokenTypeEnum,
    RawToken,
    JmespathToken,
    SubToken,
    JoinToken,
    MapToken,
    evaluate_token,
)
from rich import print as rprint

data = {
    "firstname": "John",
    "lastname": "Doe",
}


class Test:
    def _test_RawToken(self):
        token = RawToken(value="hello")
        assert token.evaluate(None) == "hello"
        assert token.evaluate("world") == "hello"
        assert token.evaluate({"key": "value"}) == "hello"
        assert token.to_dict() == {"value": "hello"}
        assert RawToken.from_dict({"value": "hello"}) == token

    def _test_JmespathToken(self):
        token = JmespathToken(path="$name")
        assert token.evaluate({"name": "John"}) == "John"
        assert token.to_dict() == {"path": "$name"}
        assert JmespathToken.from_dict({"path": "$name"}) == token

        token = JmespathToken(path="$@")
        assert token.evaluate("John") == "John"
        assert token.to_dict() == {"path": "$@"}
        assert JmespathToken.from_dict({"path": "$@"}) == token

    def _test_SubToken(self):
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

    def _test_JoinToken(self):
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

    def _test_MapToken(self):
        token = MapToken(
            key="$name",
            mapper={"alice": "$female", "bob": "$male"},
            default="unknown",
        )
        assert (
            token.evaluate({"name": "alice", "female": "girl", "male": "boy"}) == "girl"
        )
        assert token.to_dict() == {
            "key": "$name",
            "mapper": {"alice": "$female", "bob": "$male"},
            "default": "unknown",
        }
        assert (
            MapToken.from_dict(
                {
                    "key": "$name",
                    "mapper": {"alice": "$female", "bob": "$male"},
                    "default": "unknown",
                }
            )
            == token
        )

        token = MapToken(
            key="alice",
            mapper="$@",
            default="unknown",
        )
        assert token.evaluate(data={"alice": "girl"}) == "girl"

    def _test_evaluate_token(self):
        # implicit raw token
        assert evaluate_token("hello", data) == "hello"
        # implicit raw token
        assert evaluate_token([1, 2, 3], data) == [1, 2, 3]
        # implicit raw token
        assert evaluate_token({"key": "value"}, data) == {"key": "value"}
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
        # sub token
        assert (
            evaluate_token(
                {
                    "type": TokenTypeEnum.sub,
                    "kwargs": {
                        "template": "Hello {FIRSTNAME} {LASTNAME}! Today is my {AGE} years birthday!",
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
            )
            == "Hello John Doe! Today is my 18 years birthday!"
        )
        # join token
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
        # map token
        assert (
            evaluate_token(
                {
                    "type": TokenTypeEnum.map,
                    "kwargs": {
                        "key": "$name",
                        "mapper": {"alice": "$female", "bob": "$male"},
                        "default": "unknown",
                    },
                },
                {"name": "alice", "female": "girl", "male": "boy"},
            )
            == "girl"
        )

    def _test_evaluate_deeply_nested_token(self):
        token = {
            "type": TokenTypeEnum.join,
            "kwargs": {
                "sep": ", ",
                "array": [
                    {
                        "type": TokenTypeEnum.sub,
                        "kwargs": {
                            "template": "my first name is {firstname}",
                            "params": {
                                "firstname": {
                                    "type": TokenTypeEnum.sub,
                                    "kwargs": {
                                        "template": "{firstname}",
                                        "params": {
                                            "firstname": "$firstname",
                                        },
                                    },
                                },
                            },
                        },
                    },
                    {
                        "type": TokenTypeEnum.sub,
                        "kwargs": {
                            "template": "my last name is {lastname}",
                            "params": {
                                "lastname": "$lastname",
                            },
                        },
                    },
                ],
            },
        }
        value = evaluate_token(token, data)
        assert value == "my first name is John, my last name is Doe"

    def test(self):
        self._test_RawToken()
        self._test_JmespathToken()
        self._test_SubToken()
        self._test_JoinToken()
        self._test_MapToken()
        self._test_evaluate_token()
        self._test_evaluate_deeply_nested_token()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.data.token", preview=False)

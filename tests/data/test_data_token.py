# -*- coding: utf-8 -*-

from aws_resource_search.data.token import (
    StringTemplateToken,
)
from rich import print as rprint


class TestStringTemplateToken:
    def test(self):
        token = StringTemplateToken(
            template="Hello {FIRSTNAME} {LASTNAME}! Today is {DATE}.",
            params={
                "FIRSTNAME": "$first_name",
                "LASTNAME": "$last_name",
            },
        )
        value = token.evaluate(
            data={"first_name": "John", "last_name": "Doe"},
            context={"DATE": "2021-01-01"},
        )
        assert value == "Hello John Doe! Today is 2021-01-01."


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.data.token", preview=False)

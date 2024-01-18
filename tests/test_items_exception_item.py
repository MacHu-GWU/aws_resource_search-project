# -*- coding: utf-8 -*-

from aws_resource_search.items.exception_item import ExceptionItem


class TestExceptionItem:
    def test_from_error(self):
        try:
            raise ValueError("something wrong")
        except ValueError as e:
            item = ExceptionItem.from_error(error=e, uid="uid")
            assert __file__ in item.variables["traceback"]
            # ------------------------------------------------------------------
            # We only test this action manually on developer's machine, not in CI.
            # ------------------------------------------------------------------
            # item.enter_handler(ui=None)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.exception_item",
        preview=False,
    )

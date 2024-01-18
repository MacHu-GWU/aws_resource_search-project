# -*- coding: utf-8 -*-

from pathlib import Path
from aws_resource_search.items.file_item import FileItem


class TestFileItem:
    def test_from_path(self):
        item = FileItem.from_file(path=Path(__file__), uid="uid")
        assert str(item.variables["path"]) == __file__
        # ------------------------------------------------------------------
        # We only test this action manually on developer's machine, not in CI.
        # ------------------------------------------------------------------
        # item.enter_handler(ui=None)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.file_item",
        preview=False,
    )

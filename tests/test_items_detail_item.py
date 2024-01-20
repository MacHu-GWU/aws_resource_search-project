# -*- coding: utf-8 -*-

from aws_resource_search.items.detail_item import DetailItem, ExceptionItem


class TestDetailItem:
    def test_new(self):
        item = DetailItem.new(
            title="my title",
            subtitle="my subtitle",
        )
        item.enter_handler(ui=None)
        item.ctrl_a_handler(ui=None)
        assert item.variables.get("copy") is None
        assert item.variables.get("url") is None

        item = DetailItem.new(
            title="my title",
            autocomplete="autocomplete",
        )
        assert "Tab" in item.subtitle

        item = DetailItem.new(
            title="my title",
        )
        assert item.subtitle == "No subtitle"

    def test_from_detail(self):
        item = DetailItem.from_detail(
            key="key",
            value="value",
        )
        assert item.variables["copy"] == "value"
        assert item.variables["url"] is None

        item = DetailItem.from_detail(
            key="key",
            value="value",
            url="url",
        )
        assert item.variables["copy"] == "value"
        assert item.variables["url"] == "url"

    def test_from_env_vars(self):
        item_list = DetailItem.from_env_vars(
            env_vars={"key": "value"},
            url="url",
        )
        assert len(item_list) == 1
        item_list = DetailItem.from_env_vars(
            env_vars={},
            url="url",
        )
        assert len(item_list) == 1

    def test_from_tags(self):
        item_list = DetailItem.from_tags(
            tags={"key": "value"},
            url="url",
        )
        assert len(item_list) == 1
        item_list = DetailItem.from_tags(tags={}, url="url")
        assert len(item_list) == 1

    def test_get_initial_detail_items(self):
        pass

    def test_error_handling(self):
        detail_items = []
        with DetailItem.error_handling(detail_items):
            raise ValueError("something wrong")
        assert isinstance(detail_items[0], ExceptionItem)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.items.detail_item",
        preview=False,
    )

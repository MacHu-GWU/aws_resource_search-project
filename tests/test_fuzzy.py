# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from aws_resource_search.fuzzy import (
    FuzzyMatcher,
)


@dataclasses.dataclass
class Item:
    id: int
    name: str


class ItemFuzzyMatcher(FuzzyMatcher[Item]):
    def get_name(self, item: Item) -> T.Optional[str]:
        return item.name


class TestFuzzyMatcher:
    def test(self):
        items = [
            Item(id=1, name="apple and banana and cherry"),
            Item(id=2, name="alice and bob and charlie"),
        ]
        items_mapper = {item.name: [item] for item in items}

        matcher = ItemFuzzyMatcher.from_items(items)
        assert matcher.match("apple", threshold=0)[0].id == 1
        assert matcher.match("banana", threshold=0)[0].id == 1
        assert matcher.match("cherry", threshold=0)[0].id == 1

        matcher = ItemFuzzyMatcher.from_mapper(items_mapper)
        assert matcher.match("alice", threshold=0)[0].id == 2
        assert matcher.match("bob", threshold=0)[0].id == 2
        assert matcher.match("charlie", threshold=0)[0].id == 2

        # type hint auto complete test
        item = matcher.match("apple", threshold=0)[0]
        _ = item.id
        _ = item.name

        # test edge case
        res = matcher.match("apple", threshold=100)
        assert len(res) == 0

        empty_matcher = ItemFuzzyMatcher.from_mapper({})
        res = empty_matcher.match("apple", threshold=0)
        assert len(res) == 0


if __name__ == "__main__":
    from aws_resource_search.tests import run_cov_test

    run_cov_test(__file__, "aws_resource_search.fuzzy", preview=False)

# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from fuzzywuzzy import process

Item = T.TypeVar("Item")


@dataclasses.dataclass
class FuzzyMatcher(T.Generic[Item]):
    """
    Fuzzywuzzy is awesome to match string. However, what if the item is not string?

    We can define a name for each item and use fuzzywuzzy to match the name.
    Then use the name to locate the original item. This class implements this pattern.

    :param _items: list of item you want to match
    :param _names: list of str of item name
    :param _mapper: the key is the name of the item, the value is the
        list of item that with the same name.

    You have to subclass this class and implement the :meth:`FuzzyMatcher.get_name`
     method. See doc string for more information.

    Don't directly use the constructor, use the ``from_items`` or ``from_mapper``
    factory method instead.
    """

    _items: T.List[Item] = dataclasses.field(default_factory=list)
    _names: T.List[str] = dataclasses.field(default_factory=list)
    _mapper: T.Dict[str, T.List[Item]] = dataclasses.field(default_factory=dict)

    def get_name(self, item: Item) -> T.Optional[str]:
        """
        Given an item, return the item of the entity for fuzzy match.

        This method should not raise any error and always return a string or None.
        """
        raise NotImplementedError

    def _build_mapper(self):
        if self._mapper:
            self._names = list(self._mapper)
        else:
            for item in self._items:
                name = self.get_name(item)
                if name is not None:
                    self._names.append(name)
                    try:
                        self._mapper[name].append(item)
                    except:
                        self._mapper[name] = [item]

    def __post_init__(self):
        self._build_mapper()

    @classmethod
    def from_items(cls, items: T.List[Item]):
        return cls(_items=items)

    @classmethod
    def from_mapper(cls, name_to_item_mapper: T.Dict[str, T.List[Item]]):
        return cls(_mapper=name_to_item_mapper)

    def match(
        self,
        name: str,
        threshold: int = 70,
        limit: int = 5,
        filter_func: T.Callable = lambda x: True,
    ) -> T.List[Item]:
        matched_name_list = process.extract(name, self._names, limit=limit)
        if len(matched_name_list) == 0:
            return []
        matched_name_list = list(filter(filter_func, matched_name_list))
        best_matched_name, best_matched_score = matched_name_list[0]
        if best_matched_score >= threshold:
            return self._mapper[best_matched_name]
        else:
            return []

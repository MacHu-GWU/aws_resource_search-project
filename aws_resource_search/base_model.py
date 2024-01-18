# -*- coding: utf-8 -*-

"""
See :class:`BaseModel`.
"""

import typing as T
import dataclasses


@dataclasses.dataclass
class BaseModel:
    """
    The base class for all AWS Resource Search data model.

    .. note::

        I intentionally don't use ``better_dataclasses.DataClass`` as the base class
        here. Because the AWS Resource data container is so heavily used in the
        search and performance does really matter. The ``better_dataclasses.DataClass``
        provides additional features like auto-serialization and deserialization
        when using nested dataclass. But it will slow down the performance.
    """

    @classmethod
    def from_dict(cls, data: T.Dict[str, T.Any]):
        """
        Create a new instance from a dict.
        """
        return cls(**data)

    def to_dict(self) -> T.Dict[str, T.Any]:
        """
        Convert the instance to a dict.
        """
        return dataclasses.asdict(self)

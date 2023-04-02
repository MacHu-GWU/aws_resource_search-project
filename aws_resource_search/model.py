# -*- coding: utf-8 -*-

import typing as T
import dataclasses


@dataclasses.dataclass
class BaseModel:
    @classmethod
    def from_dict(cls, data: T.Dict[str, T.Any]):
        new_data = {}
        for field in dataclasses.fields(cls):
            if data.get(field.name) is not None:
                new_data[field.name] = data[field.name]
        return cls(**new_data)

    def to_dict(self) -> T.Dict[str, T.Any]:
        return dataclasses.asdict(self)

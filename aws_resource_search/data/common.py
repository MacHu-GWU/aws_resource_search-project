# -*- coding: utf-8 -*-

import dataclasses


class _Nothing:
    pass


NOTHING = _Nothing()


@dataclasses.dataclass
class BaseModel:
    def __post_init__(self):
        for k, v in dataclasses.asdict(self).items():
            if isinstance(v, _Nothing):
                raise ValueError(
                    f"arg {k!r} is required for "
                    f"{self.__class__.__module__}.{self.__class__.__qualname__}"
                )

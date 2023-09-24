# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import jmespath
from iterproxy import IterProxy

from .common import BaseModel, NOTHING
from .types import T_RESULT_ITEM


if T.TYPE_CHECKING:  # pragma: no cover
    from boto_session_manager import BotoSesManager


class ResultItemIterproxy(IterProxy[T_RESULT_ITEM]):
    pass


@dataclasses.dataclass
class Request(BaseModel):
    client: str = dataclasses.field(default=NOTHING)
    method: str = dataclasses.field(default=NOTHING)
    kwargs: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)
    is_paginator: bool = dataclasses.field(default=NOTHING)
    items_path: str = dataclasses.field(default=NOTHING)
    result: T.Optional[T.Dict[str, T.Any]] = dataclasses.field(default=None)

    def _select_result(
        self,
        item: T_RESULT_ITEM,
    ) -> T_RESULT_ITEM:
        if self.result is None:
            return item
        data = dict()
        for key, value in self.result.items():
            if value.startswith("$"):
                data[key] = jmespath.search(
                    value[1:],
                    item,
                )
            else:
                data[key] = value
        return data

    def _invoke(
        self,
        bsm: "BotoSesManager",
    ) -> T.Iterator[T_RESULT_ITEM]:
        boto_client = bsm.get_client(self.client)
        if self.is_paginator:
            paginator = boto_client.get_paginator(self.method)
            expr = jmespath.compile(self.items_path[1:])
            for response in paginator.paginate(**self.kwargs):
                for item in expr.search(response):
                    yield self._select_result(item)
        else:
            method = getattr(boto_client, self.method)
            response = method(**self.kwargs)
            expr = jmespath.compile(self.items_path[1:])
            for item in expr.search(response):
                yield self._select_result(item)

    def invoke(
        self,
        bsm: "BotoSesManager",
    ) -> ResultItemIterproxy:
        return ResultItemIterproxy(self._invoke(bsm))

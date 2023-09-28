# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses
from pathlib import Path

from diskcache import Cache
import aws_console_url.api as aws_console_url

from .compat import cached_property
from .paths import path_data_json, dir_index, dir_cache
from .vendor.hierarchy_config import apply_shared_value
from .resource_searcher import ResourceSearcher
from aws_resource_search.data.request import parse_req_json_node
from aws_resource_search.data.output import parse_out_json_node
from aws_resource_search.data.document import parse_doc_json_node
from aws_resource_search.data.url import parse_url_json_node

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager


@dataclasses.dataclass
class ARSBase:
    bsm: "BotoSesManager" = dataclasses.field()
    dir_index: Path = dataclasses.field(default=dir_index)
    dir_cache: Path = dataclasses.field(default=dir_cache)
    cache: Cache = dataclasses.field(default=None)

    def __post_init__(self):
        self.dir_index = Path(self.dir_index)
        if self.dir_cache is not None:  # pragma: no cover
            self.dir_cache = Path(self.dir_cache)
        if self.cache is None:  # pragma: no cover
            self.cache = Cache(str(self.dir_cache))
        else:
            self.dir_cache = Path(self.cache.directory)

    @cached_property
    def aws_console(self) -> aws_console_url.AWSConsole:
        return aws_console_url.AWSConsole(
            aws_account_id=self.bsm.aws_account_id,
            aws_region=self.bsm.aws_region,
            bsm=self.bsm,
        )

    @cached_property
    def _data(self):
        data = json.loads(path_data_json.read_text())
        apply_shared_value(data)
        return data

    def _get_rs(self, service_id: str, resource_type: str):
        """
        Get :class:`~aws_resource_search.resource_searcher.ResourceSearcher`
        instance by ``service_id`` and ``resource_type``. It read the data
        and construct the instance from the data.
        """
        dct = self._data[service_id][f"{service_id}-{resource_type}"]
        dct["req"]["client"] = service_id
        rs = ResourceSearcher(
            bsm=self.bsm,
            aws_console=self.aws_console,
            dir_index=self.dir_index,
            dir_cache=self.dir_cache,
            cache=self.cache,
            service_id=service_id,
            resource_type=resource_type,
            request=parse_req_json_node(dct["req"]),
            output=parse_out_json_node(dct["out"]),
            document=parse_doc_json_node(dct["doc"]),
            url=parse_url_json_node(dct["url"]),
        )
        return rs

    def _service_id_and_resource_type_pairs(
        self,
    ) -> T.List[T.Tuple[str, str]]:  # pragma: no cover
        pairs = list()
        for service_id, dct in self._data.items():
            if not service_id.startswith("_"):
                for resource_type in dct:
                    if not resource_type.startswith("_"):
                        if resource_type.startswith(f"{service_id}-"):
                            resource_type = resource_type[len(service_id) + 1 :]
                        pairs.append((service_id, resource_type))
        return pairs

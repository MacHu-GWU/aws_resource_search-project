# -*- coding: utf-8 -*-

"""
Define the config class data model.
"""

import typing as T
import json
import dataclasses
from pathlib import Path

from ..vendor.json_utils import strip_comments
from ..vendor.better_dataclasses import DataClass
from ..vendor.hierarchy_config import SHARED, apply_shared_value

from ..paths import path_config_json
from ..searcher_enum import SearcherEnum


@dataclasses.dataclass
class Resource(DataClass):
    cache_expire: int = dataclasses.field()


@dataclasses.dataclass
class Config(DataClass):
    res: T.Dict[str, Resource] = Resource.map_of_nested_field(default_factory=dict)

    @classmethod
    def load(cls, path: Path = path_config_json) -> "Config":
        if path.exists():
            data = json.loads(strip_comments(path.read_text()))
            apply_shared_value(data)
            return cls.from_dict(data)
        else:
            default_cache_expire = 24 * 60 * 60

            default_data = {
                SHARED: {
                    "res.*.cache_expire": default_cache_expire,
                },
                "res": {
                    res_type.value: {
                        "cache_expire": default_cache_expire,
                    }
                    for res_type in SearcherEnum
                },
            }
            res = default_data["res"]
            res[SearcherEnum.codebuild_job_run.value]["cache_expire"] = 5 * 60
            res[SearcherEnum.ecs_task_run.value]["cache_expire"] = 5 * 60
            res[SearcherEnum.glue_job_run.value]["cache_expire"] = 5 * 60
            res[SearcherEnum.sfn_state_machine_execution.value]["cache_expire"] = 5 * 60
            path_config_json.write_text(json.dumps(default_data, indent=4))
            return cls.load(path=path)

    def get_cache_expire(self, res_type: str) -> int:
        return self.res[res_type].cache_expire

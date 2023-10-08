# -*- coding: utf-8 -*-

import typing as T
import json
import sayt.api as sayt

from .paths import dir_index, dir_cache, path_data_json


def srv_and_res_downloader() -> T.List[T.Dict[str, T.Any]]:
    data = json.loads(path_data_json.read_text())
    records = list()
    for service_id, service_dct in data.items():
        if service_id.startswith("_"):
            continue
        for resource_type, _ in service_dct.items():
            if resource_type.startswith("_"):
                continue
            records.append({"srv_and_res": resource_type})
    return records


def srv_and_res_cache_key_def(
    download_kwargs: sayt.T_KWARGS,
    context: sayt.T_CONTEXT,
):
    return ["aws-resource-search-service-and-resource"]


def srv_and_res_extractor(
    record: sayt.T_RECORD,
    download_kwargs: sayt.T_KWARGS,
    context: sayt.T_CONTEXT,
) -> sayt.T_RECORD:
    return {"id": record["srv_and_res"], "name": record["srv_and_res"], "raw": record}


srv_and_res_fields = [
    sayt.IdField(
        name="id",
        stored=True,
    ),
    sayt.NgramWordsField(
        name="name",
        stored=True,
        minsize=2,
        maxsize=6,
    ),
    sayt.StoredField(
        name="raw",
    ),
]

srv_and_res_ds = sayt.RefreshableDataSet(
    downloader=srv_and_res_downloader,
    cache_key_def=srv_and_res_cache_key_def,
    extractor=srv_and_res_extractor,
    fields=srv_and_res_fields,
    dir_index=dir_index,
    dir_cache=dir_cache,
    cache_expire=3600,
)

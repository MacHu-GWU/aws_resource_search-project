# -*- coding: utf-8 -*-

import typing as T
import sayt.api as sayt


def downloader(ec2_client) -> T.List[T.Dict[str, T.Any]]:
    paginator = ec2_client.get_paginator("describe_instances")
    for response in paginator.paginate(
        PaginationConfig={
            "MaxItems": 9999,
            "PageSize": 1000
        },
    ):

    n = 10
    return [
        {"id": ith, "name": f"{ith}th-{env}-machine"}
        for ith in range(1, 1 + n)
    ]


def cache_key_def(
    download_kwargs: T_KWARGS,
    context: T_CONTEXT,
) -> T.List[str]:
    return [download_kwargs["env"]]


# extractor is a function that converts the record into whoosh document
def extractor(
    record: T_RECORD,
    download_kwargs: T_KWARGS,
    context: T_CONTEXT,
) -> T_RECORD:
    greeting = context["greeting"]
    name = record["name"]
    return {"message": f"{greeting} {name}", "raw": record}


# we would like to use ngram search on message field
# and store the raw data as it is
fields = [
    NgramWordsField(
        name="message",
        stored=True,
        minsize=2,
        maxsize=6,
    ),
    StoredField(
        name="raw",
    ),
]

rds = RefreshableDataSet(
    downloader=downloader,
    cache_key_def=cache_key_def,
    extractor=extractor,
    fields=fields,
    dir_index=Path("/path/to/index"),
    dir_cache=Path("/path/to/cache"),
    cache_expire=3600,
    context={"greeting": "Hello"},
)

result = rds.search(
    download_kwargs={"env": "dev"},
    query="dev",
)

print(result)
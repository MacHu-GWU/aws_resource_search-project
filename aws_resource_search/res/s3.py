# -*- coding: utf-8 -*-

import dataclasses
from .. import res_lib


@dataclasses.dataclass
class S3Bucket(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    creation_date: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource: res_lib.T_RESULT_DATA):
        return cls(
            raw_data=resource,
            id=resource["Name"],
            name=resource["Name"],
            creation_date=resource["CreationDate"].isoformat(),
        )

    @property
    def title(self) -> str:
        return self.name

    @property
    def subtitle(self) -> str:
        return self.creation_date

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return f"arn:aws:s3:::{self.name}"

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.s3.get_console_url(bucket=self.name)


s3_bucket_searcher = res_lib.Searcher(
    # list resources
    service="s3",
    method="list_buckets",
    is_paginator=False,
    default_boto_kwargs=None,
    result_path=res_lib.ResultPath("Buckets"),
    # extract document
    doc_class=S3Bucket,
    # search
    resource_type="s3-bucket",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="creation_date"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import zelfred.api as zf

from .. import res_lib

if T.TYPE_CHECKING:
    from ..ars_v2 import ARS


@dataclasses.dataclass
class S3Bucket(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    creation_date: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
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
        return f"<create_at>: {self.creation_date}"

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return f"arn:aws:s3:::{self.name}"

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.s3.get_console_url(bucket=self.name)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        res = ars.bsm.s3_client.get_bucket_location(Bucket=self.name)
        location = res["LocationConstraint"]

        res = ars.bsm.s3_client.get_bucket_tagging(Bucket=self.name)
        tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("TagSet", [])}
        tag_items = res_lib.DetailItem.from_tags(tags)

        return [
            res_lib.DetailItem(
                title=f"<s3 uri>: s3://{self.name}",
                subtitle="📋 Tap 'Ctrl + A' to copy to clipboard",
                uid="uri",
                variables={
                    "copy": f"s3://{self.name}",
                    "url": None,
                },
            ),
            res_lib.DetailItem(
                title=f"<s3 arn>: {self.arn}",
                subtitle="📋 Tap 'Ctrl + A' to copy to clipboard",
                uid="arn",
                variables={
                    "copy": self.arn,
                    "url": None,
                },
                arg=self.arn,
            ),
            res_lib.DetailItem(
                title=f"<location>: {location}",
                subtitle="📋 Tap 'Ctrl + A' to copy.",
                uid="location",
                variables={
                    "copy": location,
                    "url": None,
                },
            ),
            *tag_items,
        ]


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

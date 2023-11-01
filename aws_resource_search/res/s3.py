# -*- coding: utf-8 -*-

"""
S3 resources.
"""

import typing as T
import dataclasses

from .. import res_lib
from ..terminal import format_key_value

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class S3Bucket(res_lib.BaseDocument):
    """
    S3 Bucket resource data model.
    """

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
        """
        Example: :cyan:`bucket_name` = :yellow:`my-bucket`
        """
        return format_key_value("bucket_name", self.name)

    @property
    def subtitle(self) -> str:
        """
        Example: :cyan:`create_at` = :yellow:`2021-07-06T15:04:40+00:00`,
        🌐 :magenta:`Enter`, 📋 :magenta:`Ctrl A`, 🔗 :magenta:`Ctrl U`, 👀 :magenta:`Ctrl P`.
        """
        return "{}, {}".format(
            format_key_value("create_at", self.creation_date),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        """
        Automatically enter the bucket name.
        """
        return self.name

    @property
    def arn(self) -> str:
        """
        Example: ``arn:aws:s3:::my-bucket``
        """
        return f"arn:aws:s3:::{self.name}"

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.s3.get_console_url(bucket=self.name)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        """
        Include s3 uri, s3 arn, bucket location and tags in details.
        """
        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        url = self.get_console_url(aws)
        detail_items = [
            Item("s3 uri", f"s3://{self.name}", url=url),
            Item("s3 arn", self.arn, url=url),
        ]

        with self.enrich_details(detail_items):
            res = ars.bsm.s3_client.get_bucket_location(Bucket=self.name)
            location = res["LocationConstraint"]
            if not location:
                location = "us-east-1"
            detail_items.append(Item("location", location))

        with self.enrich_details(detail_items):
            res = ars.bsm.s3_client.get_bucket_policy(Bucket=self.name)
            detail_items.append(Item("bucket_policy", self.one_line(res.get("Policy", "{}"))))

        with self.enrich_details(detail_items):
            res = ars.bsm.s3_client.get_bucket_tagging(Bucket=self.name)
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("TagSet", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items


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

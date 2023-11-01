# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses

from .. import res_lib
from ..terminal import format_key_value

if T.TYPE_CHECKING:
    from ..ars import ARS


def normalize_alias(alias: str) -> str:
    if alias.startswith("alias/"):
        return alias[6:]
    else:
        return alias


@dataclasses.dataclass
class KmsAlias(res_lib.BaseDocument):
    key_id: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    alias_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            key_id=resource.get("TargetKeyId", "NA"),
            id=normalize_alias(resource["AliasName"]),
            name=normalize_alias(resource["AliasName"]),
            alias_arn=resource["AliasArn"],
        )

    @property
    def title(self) -> str:
        return format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}".format(
            format_key_value("key_id", self.key_id),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.alias_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.kms.get_key(key_id_or_alias_or_arn=self.key_id)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        detail_items.extend([
            Item("KeyId", self.raw_data.get("TargetKeyId", "NA"), url=self.get_console_url(ars.aws_console)),
            Item("CreationDate", self.raw_data.get("RotationLambdaARN", "NA")),
            Item("LastUpdatedDate", self.raw_data.get("RotationEnabled", "NA")),
        ])

        with self.enrich_details(detail_items):
            res = ars.bsm.kms_client.describe_key(KeyId=self.key_id)
            dct = res["KeyMetadata"]
            detail_items.extend([
                Item("KeyState", dct.get("KeyState", "NA")),
                Item("KeyManager", dct.get("KeyManager", "NA")),
            ])

        with self.enrich_details(detail_items):
            res = ars.bsm.kms_client.list_resource_tags(KeyId=self.key_id)
            tags: dict = {dct["TagKey"]: dct["TagValue"] for dct in self.raw_data.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))
        return detail_items
    # fmt: on


kms_key_alias_searcher = res_lib.Searcher(
    # list resources
    service="kms",
    method="list_aliases",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {"MaxItems": 9999, "PageSize": 1000},
    },
    result_path=res_lib.ResultPath("Aliases"),
    # extract document
    doc_class=KmsAlias,
    # search
    resource_type="kms-alias",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="key_id"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="alias_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

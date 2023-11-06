# -*- coding: utf-8 -*-

"""
Key Management Service (KMS) related resources.
"""

import typing as T
import dataclasses

from .. import res_lib
from ..terminal import format_key_value
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


def normalize_alias(alias: str) -> str:
    if alias.startswith("alias/"):
        return alias[6:]
    else:
        return alias


@dataclasses.dataclass
class KmsKeyAlias(res_lib.BaseDocument):
    key_id: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=normalize_alias(resource["AliasName"]),
            name=normalize_alias(resource["AliasName"]),
            key_id=resource.get("TargetKeyId", "NA"),
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
        return self.raw_data["AliasArn"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.kms.get_key(key_id_or_alias_or_arn=self.key_id)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        detail_items.extend([
            from_detail("KeyId", self.raw_data.get("TargetKeyId", "NA"), url=url),
        ])

        with self.enrich_details(detail_items):
            res = ars.bsm.kms_client.describe_key(KeyId=self.key_id)
            dct = res["KeyMetadata"]
            detail_items.extend([
                from_detail("KeyManager", dct.get("KeyManager", "NA"), url=url),
                from_detail("Description", dct.get("Description", "No description"), url=url),
                from_detail("CreationDate", dct.get("CreationDate", "NA"), url=url),
                from_detail("DeletionDate", dct.get("DeletionDate", "NA"), url=url),
                from_detail("ValidTo", dct.get("ValidTo", "NA"), url=url),
                from_detail("KeyState", dct.get("KeyState", "NA"), url=url),
                from_detail("KeyUsage", dct.get("KeyUsage", "NA"), url=url),
            ])

        with self.enrich_details(detail_items):
            res = ars.bsm.kms_client.list_resource_tags(KeyId=self.key_id)
            tags: dict = {dct["TagKey"]: dct["TagValue"] for dct in res.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))
        return detail_items
    # fmt: on


class KmsKeyAliasSearcher(res_lib.Searcher[KmsKeyAlias]):
    pass


kms_key_alias_searcher = KmsKeyAliasSearcher(
    # list resources
    service="kms",
    method="list_aliases",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {"MaxItems": 9999, "PageSize": 1000},
    },
    result_path=res_lib.ResultPath("Aliases"),
    # extract document
    doc_class=KmsKeyAlias,
    # search
    resource_type=SearcherEnum.kms_key_alias,
    fields=res_lib.define_fields(
        fields=[
            res_lib.sayt.NgramWordsField(name="key_id", minsize=2, maxsize=4, stored=True),
        ],
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

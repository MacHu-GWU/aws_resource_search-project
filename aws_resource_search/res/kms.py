# -*- coding: utf-8 -*-

"""
Key Management Service (KMS) related resources.
"""

import typing as T
import dataclasses

import sayt.api as sayt
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


def normalize_alias(alias: str) -> str:
    if alias.startswith("alias/"):
        return alias[6:]
    else:
        return alias


@dataclasses.dataclass
class KmsKeyAlias(rl.ResourceDocument):
    # fmt: off
    key_id: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="key_id", minsize=2, maxsize=4, stored=True)})
    # fmt: on

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
        return rl.format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}".format(
            rl.format_key_value("key_id", self.key_id),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data["AliasArn"]

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.kms.get_key(key_id_or_alias_or_arn=self.key_id)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.kms.customer_managed_keys

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        detail_items.extend([
            from_detail("KeyId", self.raw_data.get("TargetKeyId", "NA"), url=url),
        ])

        with rl.DetailItem.error_handling(detail_items):
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

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.kms_client.list_resource_tags(KeyId=self.key_id)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))
        return detail_items
    # fmt: on


class KmsKeyAliasSearcher(rl.BaseSearcher[KmsKeyAlias]):
    pass


kms_key_alias_searcher = KmsKeyAliasSearcher(
    # list resources
    service="kms",
    method="list_aliases",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {"MaxItems": 9999, "PageSize": 1000},
    },
    result_path=rl.ResultPath("Aliases"),
    # extract document
    doc_class=KmsKeyAlias,
    # search
    resource_type=rl.SearcherEnum.kms_key_alias.value,
    fields=KmsKeyAlias.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.kms_key_alias.value),
    more_cache_key=None,
)

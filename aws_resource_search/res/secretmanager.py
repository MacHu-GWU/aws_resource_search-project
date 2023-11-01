# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses

from .. import res_lib
from ..terminal import format_key_value

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class SecretsManagerSecret(res_lib.BaseDocument):
    description: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    secret_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            description=resource.get("Description", "No description"),
            id=resource["Name"],
            name=resource["Name"],
            secret_arn=resource["ARN"],
        )

    @property
    def title(self) -> str:
        return format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}".format(
            self.description,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.secret_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.secretmanager.get_secret(secret_name_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars, arn_field_name="statemachine_arn")

        with self.enrich_details(detail_items):
            detail_items.extend([
                Item("KmsKeyId", self.raw_data.get("KmsKeyId", "NA")),
                Item("RotationEnabled", self.raw_data.get("RotationEnabled", "NA")),
                Item("RotationLambdaARN", self.raw_data.get("RotationLambdaARN", "NA")),
                Item("RotationRules", json.dumps(self.raw_data.get("RotationRules", {}))),
                Item("LastRotatedDate", self.raw_data.get("LastRotatedDate", "NA")),
                Item("LastChangedDate", self.raw_data.get("LastChangedDate", "NA")),
                Item("LastAccessedDate", self.raw_data.get("LastAccessedDate", "NA")),
                Item("DeletedDate", self.raw_data.get("DeletedDate", "NA")),
                Item("NextRotationDate", self.raw_data.get("NextRotationDate", "NA")),
                Item("OwningService", self.raw_data.get("OwningService", "NA")),
                Item("CreatedDate", self.raw_data.get("CreatedDate", "NA")),
                Item("PrimaryRegion", self.raw_data.get("PrimaryRegion", "NA")),
            ])

            tags: dict = {dct["key"]: dct["value"] for dct in self.raw_data.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items
    # fmt: on


secretsmanager_secret_searcher = res_lib.Searcher(
    # list resources
    service="secretsmanager",
    method="list_secrets",
    is_paginator=True,
    default_boto_kwargs={
        "IncludePlannedDeletion": True,
        "SortOrder": "desc",
        "PaginationConfig": {"MaxItems": 9999, "PageSize": 100},
    },
    result_path=res_lib.ResultPath("SecretList"),
    # extract document
    doc_class=SecretsManagerSecret,
    # search
    resource_type="secretsmanager-secret",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="description"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="secret_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

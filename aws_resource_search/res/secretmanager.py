# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses

from .. import res_lib
from ..terminal import format_key_value
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class SecretsManagerSecret(res_lib.BaseDocument):
    @property
    def description(self) -> str:
        return res_lib.get_description(self.raw_data, "Description")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["Name"],
            name=resource["Name"],
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
        return self.raw_data["ARN"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.secretmanager.get_secret(secret_name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_details = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(
            ars, arn_field_name="statemachine_arn"
        )
        url = self.get_console_url(ars.aws_console)

        # fmt: off
        with self.enrich_details(detail_items):
            res = ars.bsm.secretsmanager_client.describe_secret(SecretId=self.name)
            detail_items.extend([
                from_details("KmsKeyId", res.get("KmsKeyId", "NA"), url=url),
                from_details("RotationEnabled", res.get("RotationEnabled", "NA"), url=url),
                from_details("RotationLambdaARN", res.get("RotationLambdaARN", "NA"), url=url),
                from_details("RotationRules", json.dumps(res.get("RotationRules", {})), url=url),
                from_details("LastRotatedDate", res.get("LastRotatedDate", "NA"), url=url),
                from_details("LastChangedDate", res.get("LastChangedDate", "NA"), url=url),
                from_details("LastAccessedDate", res.get("LastAccessedDate", "NA"), url=url),
                from_details("DeletedDate", res.get("DeletedDate", "NA"), url=url),
                from_details("NextRotationDate", res.get("NextRotationDate", "NA"), url=url),
                from_details("OwningService", res.get("OwningService", "NA"), url=url),
                from_details("CreatedDate", res.get("CreatedDate", "NA"), url=url),
                from_details("PrimaryRegion", res.get("PrimaryRegion", "NA"), url=url),
            ])
            # fmt: on
            tags: dict = {dct["key"]: dct["value"] for dct in self.raw_data.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

        return detail_items


class SecretsManagerSecretSearcher(res_lib.Searcher[SecretsManagerSecret]):
    pass


secretsmanager_secret_searcher = SecretsManagerSecretSearcher(
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
    resource_type=SearcherEnum.secretsmanager_secret,
    fields=res_lib.define_fields(),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

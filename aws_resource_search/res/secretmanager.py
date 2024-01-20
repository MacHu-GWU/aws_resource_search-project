# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses

import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


@dataclasses.dataclass
class SecretsManagerSecret(rl.ResourceDocument):
    @property
    def description(self) -> str:
        return rl.get_description(self.raw_data, "Description")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["Name"],
            name=resource["Name"],
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("name", self.name)

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

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.secretmanager.get_secret(secret_name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.secretmanager.secrets

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_details = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
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
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class SecretsManagerSecretSearcher(rl.BaseSearcher[SecretsManagerSecret]):
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
    result_path=rl.ResultPath("SecretList"),
    # extract document
    doc_class=SecretsManagerSecret,
    # search
    resource_type=rl.SearcherEnum.secretsmanager_secret.value,
    fields=SecretsManagerSecret.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(
        rl.SearcherEnum.secretsmanager_secret.value
    ),
    more_cache_key=None,
)

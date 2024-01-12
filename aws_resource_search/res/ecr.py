# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class EcrRepository(res_lib.BaseDocument):
    uri: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["repositoryName"],
            name=resource["repositoryName"],
            uri=resource["repositoryUri"],
        )

    @property
    def title(self) -> str:
        return format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}".format(
            self.uri,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data["repositoryArn"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.ecr.get_repo(name_or_arn_or_uri=self.arn)

    @property
    def registry_id(self) -> str:
        return self.raw_data["registryId"]

    @property
    def repository_name(self) -> str:
        return self.raw_data["repositoryName"]

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            detail_items.extend(
                # fmt: off
                [
                    from_detail("registry_id", self.registry_id, url=url),
                    from_detail("repository_name", self.repository_name, url=url),
                    from_detail("repository_uri", self.raw_data["repositoryUri"], url=url),
                    from_detail("repository_arn", self.raw_data["repositoryArn"], url=url),
                    from_detail("create_at", self.raw_data["createdAt"], url=url),
                    from_detail("image_tag_mutability", self.raw_data["imageTagMutability"], url=url),
                ]
                # fmt: on
            )
            res = ars.bsm.ecr_client.get_repository_policy(
                registryId=self.registry_id,
                repositoryName=self.repository_name,
            )
            # fmt: off
            detail_items.extend([
                from_detail("repo_policy", self.one_line(res.get("policyText", "{}")), url=url),
            ])
            # fmt: on
            res = ars.bsm.ecr_client.list_tags_for_resource(resourceArn=self.arn)
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url=url))
        return detail_items


class EcrRepositorySearcher(res_lib.Searcher[EcrRepository]):
    pass


ecr_repository_searcher = EcrRepositorySearcher(
    # list resources
    service="ecr",
    method="describe_repositories",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("repositories"),
    # extract document
    doc_class=EcrRepository,
    # search
    resource_type=SearcherEnum.ecr_repository,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.StoredField(name="uri"),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class EcrRepositoryImage(res_lib.BaseDocument):
    repo_arn: str = dataclasses.field()
    repo_uri: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        ecr_repo = arns.res.EcrRepository.new(
            aws_account_id=resource["registryId"],
            aws_region=bsm.aws_region,
            repo_name=resource["repositoryName"],
        )
        return cls(
            raw_data=resource,
            id=resource["imageDigest"].split(":")[-1],
            name=", ".join(resource.get("imageTags", [])),
            repo_arn=ecr_repo.to_arn(),
            repo_uri=ecr_repo.uri,
        )

    @property
    def title(self) -> str:
        return "{}, {}".format(
            format_key_value("digest", self.id),
            format_key_value("tags", self.name),
        )

    @property
    def subtitle(self) -> str:
        return "{}".format(
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return f"{self.repository_name}@{self.id}"

    @property
    def arn(self) -> str:
        return f"{self.repo_arn}:{self.id}"

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        # todo: add image url support to aws_console_url project
        origin_digest = self.raw_data["imageDigest"]
        return (
            f"https://{console.aws_region}.console.aws.amazon.com/ecr/repositories/private"
            f"/{self.registry_id}/{self.repository_name}/_"
            f"/image/{origin_digest}/details"
        )

    @property
    def digest(self) -> str:
        return self.id

    @property
    def registry_id(self) -> str:
        return self.raw_data["registryId"]

    @property
    def repository_name(self) -> str:
        return self.raw_data["repositoryName"]

    @property
    def image_tags(self) -> T.List[str]:
        return self.raw_data.get("imageTags", [])

    @property
    def uri(self) -> str:
        return f"{self.repo_uri}:{self.digest}"

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            detail_items.extend(
                # fmt: off
                [
                    from_detail("registry_id", self.registry_id, url=url),
                    from_detail("repository_name", self.repository_name, url=url),
                    from_detail("repository_uri", self.repo_uri, url=url),
                    from_detail("repository_arn", self.repo_arn, url=url),
                    from_detail("image_pushed_at", self.raw_data["imagePushedAt"], url=url),
                    from_detail("last_recorded_pull_time", self.raw_data.get("lastRecordedPullTime", "NA"), url=url),
                    from_detail("image_scan_status", self.raw_data.get("imageScanStatus", {}).get("status", "NA"), url=url),
                ]
                # fmt: on
            )
            for image_tag in self.image_tags:
                detail_items.append(from_detail(f"image_tag", image_tag, url=url))
        return detail_items


class EcrRepositoryImageSearcher(res_lib.Searcher[EcrRepositoryImage]):
    pass


ecr_repository_image_searcher = EcrRepositoryImageSearcher(
    # list resources
    service="ecr",
    method="describe_images",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("imageDetails"),
    # extract document
    doc_class=EcrRepositoryImage,
    # search
    resource_type=SearcherEnum.ecr_repository_image,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.StoredField(name="repo_arn"),
            res_lib.sayt.StoredField(name="repo_uri"),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=lambda boto_kwargs: [boto_kwargs["repositoryName"]],
)

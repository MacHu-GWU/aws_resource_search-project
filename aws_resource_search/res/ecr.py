# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import sayt.api as sayt
import aws_arns.api as arns
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


@dataclasses.dataclass
class EcrRepository(rl.ResourceDocument):
    # fmt: off
    uri: str = dataclasses.field(metadata={"field": sayt.StoredField(name="uri")})
    # fmt: on

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
        return rl.format_key_value("name", self.name)

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

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.ecr.get_repo(name_or_arn_or_uri=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.ecr.repos

    @property
    def registry_id(self) -> str:
        return self.raw_data["registryId"]

    @property
    def repository_name(self) -> str:
        return self.raw_data["repositoryName"]

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            detail_items.extend(
                [
                    from_detail("registry_id", self.registry_id, url=url),
                    from_detail("repository_name", self.repository_name, url=url),
                    from_detail("repository_uri", self.raw_data["repositoryUri"], url=url),
                    from_detail("repository_arn", self.raw_data["repositoryArn"], url=url),
                    from_detail("create_at", self.raw_data["createdAt"], url=url),
                    from_detail("image_tag_mutability", self.raw_data["imageTagMutability"], url=url),
                ]
            )
            res = ars.bsm.ecr_client.get_repository_policy(
                registryId=self.registry_id,
                repositoryName=self.repository_name,
            )

            detail_items.extend([
                from_detail("repo_policy", self.one_line(res.get("policyText", "{}")), url=url),
            ])
            res = ars.bsm.ecr_client.list_tags_for_resource(resourceArn=self.arn)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url=url))
        return detail_items
    # fmt: on


class EcrRepositorySearcher(rl.BaseSearcher[EcrRepository]):
    pass


ecr_repository_searcher = EcrRepositorySearcher(
    # list resources
    service="ecr",
    method="describe_repositories",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("repositories"),
    # extract document
    doc_class=EcrRepository,
    # search
    resource_type=rl.SearcherEnum.ecr_repository.value,
    fields=EcrRepository.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.ecr_repository.value),
    more_cache_key=None,
)


@dataclasses.dataclass
class EcrRepositoryImage(rl.ResourceDocument):
    # fmt: off
    repo_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="repo_arn")})
    repo_uri: str = dataclasses.field(metadata={"field": sayt.StoredField(name="repo_uri")})
    # fmt: on

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
            rl.format_key_value("digest", self.id),
            rl.format_key_value("tags", self.name),
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

    def get_console_url(self, console: acu.AWSConsole) -> str:
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

    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
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


class EcrRepositoryImageSearcher(rl.BaseSearcher[EcrRepositoryImage]):
    pass


ecr_repository_image_searcher = EcrRepositoryImageSearcher(
    # list resources
    service="ecr",
    method="describe_images",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("imageDetails"),
    # extract document
    doc_class=EcrRepositoryImage,
    # search
    resource_type=rl.SearcherEnum.ecr_repository_image.value,
    fields=EcrRepositoryImage.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.ecr_repository_image.value),
    more_cache_key=lambda boto_kwargs: [boto_kwargs["repositoryName"]],
)

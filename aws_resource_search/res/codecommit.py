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
class CodeCommitRepository(rl.ResourceDocument):
    # fmt: off
    repo_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="repo_arn")})
    # fmt: on

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["repositoryName"],
            name=resource["repositoryName"],
            repo_arn=arns.res.CodeCommitRepository.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                name=resource["repositoryName"],
            ).to_arn(),
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("repo_name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.repo_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.codecommit.get_repo(repo_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.codecommit.repositories

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)
        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.codecommit_client.get_repository(repositoryName=self.name)
            dct = res["repositoryMetadata"]
            accountId = dct.get("accountId")
            repositoryId = dct.get("repositoryId")
            repositoryName = dct.get("repositoryName")
            repositoryDescription = dct.get("repositoryDescription")
            defaultBranch = dct.get("defaultBranch")
            lastModifiedDate = dct.get("lastModifiedDate")
            creationDate = dct.get("creationDate")
            cloneUrlHttp = dct.get("cloneUrlHttp")
            cloneUrlSsh = dct.get("cloneUrlSsh")
            detail_items.extend([
                from_detail("accountId", accountId, url=url),
                from_detail("repositoryId", repositoryId, url=url),
                from_detail("repositoryName", repositoryName, url=url),
                from_detail("repositoryDescription", self.one_line(repositoryDescription), url=url),
                from_detail("defaultBranch", defaultBranch, url=url),
                from_detail("lastModifiedDate", lastModifiedDate, url=url),
                from_detail("creationDate", creationDate, url=url),
                from_detail("cloneUrlHttp", cloneUrlHttp, url=url),
                from_detail("cloneUrlSsh", cloneUrlSsh, url=url),
                from_detail("cloneUrlGitRemoteCodecommit", f"codecommit::{ars.bsm.aws_region}://{self.name}", url=url)
            ])

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.codecommit_client.list_tags_for_resource(resourceArn=self.arn)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class CodeCommitRepositorySearcher(rl.BaseSearcher[CodeCommitRepository]):
    pass


codecommit_repository_searcher = CodeCommitRepositorySearcher(
    # list resources
    service="codecommit",
    method="list_repositories",
    is_paginator=True,
    default_boto_kwargs={
        "sortBy": "lastModifiedDate",
        "order": "descending",
        "PaginationConfig": {
            "MaxItems": 5000,
        },
    },
    result_path=rl.ResultPath("repositories"),
    # extract document
    doc_class=CodeCommitRepository,
    # search
    resource_type=rl.SearcherEnum.codecommit_repository.value,
    fields=CodeCommitRepository.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(
        rl.SearcherEnum.codecommit_repository.value
    ),
    more_cache_key=None,
)

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
class CodeCommitRepository(res_lib.BaseDocument):
    repo_arn: str = dataclasses.field()

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
        return format_key_value("repo_name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.repo_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.codecommit.get_repo(repo_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)
        with self.enrich_details(detail_items):
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

        with self.enrich_details(detail_items):
            res = ars.bsm.codecommit_client.list_tags_for_resource(resourceArn=self.arn)
            tags: dict = res["tags"]
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class CodeCommitRepositorySearcher(res_lib.Searcher[CodeCommitRepository]):
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
    result_path=res_lib.ResultPath("repositories"),
    # extract document
    doc_class=CodeCommitRepository,
    # search
    resource_type=SearcherEnum.codecommit_repository,
    fields=res_lib.define_fields(
        fields=[
            res_lib.sayt.StoredField(name="repo_arn"),
        ]
    ),
    cache_expire=7 * 24 * 60 * 60,
    more_cache_key=None,
)

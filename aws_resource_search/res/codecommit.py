# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class CodeCommitRepository(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
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
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)

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
                Item("accountId", accountId),
                Item("repositoryId", repositoryId),
                Item("repositoryName", repositoryName),
                Item("repositoryDescription", self.one_line(repositoryDescription)),
                Item("defaultBranch", defaultBranch),
                Item("lastModifiedDate", lastModifiedDate),
                Item("creationDate", creationDate),
                Item("cloneUrlHttp", cloneUrlHttp),
                Item("cloneUrlSsh", cloneUrlSsh),
            ])
            detail_items.append(
                Item("cloneUrlGitRemoteCodecommit", f"codecommit::{ars.bsm.aws_region}://{self.name}")
            )

        with self.enrich_details(detail_items):
            res = ars.bsm.codecommit_client.list_tags_for_resource(resourceArn=self.arn)
            tags: dict = res["tags"]
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items
    # fmt: on


codecommit_repository_searcher = res_lib.Searcher(
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
    resource_type="codecommit-repository",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="repo_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

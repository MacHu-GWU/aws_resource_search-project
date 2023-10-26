# -*- coding: utf-8 -*-

import dataclasses

import aws_arns.api as arns

from .. import res_lib


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
        return self.name

    @property
    def subtitle(self) -> str:
        return "Tap 'Enter' to open it in AWS Console"

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.repo_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.codecommit.get_repo(repo_or_arn=self.arn)


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

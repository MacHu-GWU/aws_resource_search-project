# -*- coding: utf-8 -*-

import dataclasses
from .. import res_lib


@dataclasses.dataclass
class IamRole(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    role_arn: str = dataclasses.field()
    create_date: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource: res_lib.T_RESULT_DATA):
        return cls(
            raw_data=resource,
            id=resource["RoleName"],
            name=resource["RoleName"],
            role_arn=resource["Arn"],
            create_date=resource["CreateDate"].isoformat(),
        )

    @property
    def title(self) -> str:
        return self.name

    @property
    def subtitle(self) -> str:
        return self.create_date

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.role_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_role(name_or_arn=self.role_arn)


iam_role_searcher = res_lib.Searcher(
    # list resources
    service="iam",
    method="list_roles",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Roles"),
    # extract document
    doc_class=IamRole,
    # search
    resource_type="iam-role",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="role_arn"),
        res_lib.sayt.StoredField(name="create_date"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

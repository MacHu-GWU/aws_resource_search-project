# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses

import aws_arns.api as arns

from .. import res_lib

if T.TYPE_CHECKING:
    from ..ars_v2 import ARS


def extract_datetime(resource: res_lib.T_RESULT_DATA) -> str:
    return res_lib.extract_datetime(resource, "CreateDate", "No CreateDate")


@dataclasses.dataclass
class IamGroup(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    group_arn: str = dataclasses.field()
    create_date: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["GroupName"],
            name=resource["GroupName"],
            group_arn=resource["Arn"],
            create_date=extract_datetime(resource),
        )

    @property
    def title(self) -> str:
        return self.name

    @property
    def subtitle(self) -> str:
        return f"<create_at>: {self.create_date}, <arn>: {self.arn}"

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.group_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_user_group(name_or_arn=self.arn)


iam_group_searcher = res_lib.Searcher(
    # list resources
    service="iam",
    method="list_groups",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Groups"),
    # extract document
    doc_class=IamGroup,
    # search
    resource_type="iam-group",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="group_arn"),
        res_lib.sayt.StoredField(name="create_date"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class IamUser(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    user_arn: str = dataclasses.field()
    create_date: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["UserName"],
            name=resource["UserName"],
            user_arn=resource["Arn"],
            create_date=extract_datetime(resource),
        )

    @property
    def title(self) -> str:
        return self.name

    @property
    def subtitle(self) -> str:
        return f"<create_at>: {self.create_date}, <arn>: {self.arn}"

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.user_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_user(name_or_arn=self.arn)


iam_user_searcher = res_lib.Searcher(
    # list resources
    service="iam",
    method="list_users",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Users"),
    # extract document
    doc_class=IamUser,
    # search
    resource_type="iam-user",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="user_arn"),
        res_lib.sayt.StoredField(name="create_date"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class IamRole(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    role_arn: str = dataclasses.field()
    create_date: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["RoleName"],
            name=resource["RoleName"],
            role_arn=resource["Arn"],
            create_date=extract_datetime(resource),
        )

    def is_service_role(self) -> bool:
        return "/aws-service-role/" in self.role_arn

    @property
    def title(self) -> str:
        if self.is_service_role():
            return f"🪖 {self.name}"
        else:
            return f"🧢 {self.name}"

    @property
    def subtitle(self) -> str:
        return f"<create_at>: {self.create_date}, <arn>: {self.arn}"

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.role_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_role(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        role_id = self.raw_data["RoleId"]
        assume_role_policy_document: dict = self.raw_data["AssumeRolePolicyDocument"]

        res = ars.bsm.iam_client.list_attached_role_policies(
            RoleName=self.name, MaxItems=50
        )
        managed_policy_items = [
            res_lib.DetailItem(
                title="<managed policy>: {}".format(dct["PolicyName"]),
                subtitle="🌐 Tap 'Enter' to open url, 📋 tap 'Ctrl + A' to copy",
                uid="policy {}".format(dct["PolicyArn"]),
                variables={
                    "url": ars.aws_console.iam.get_policy(name_or_arn=dct["PolicyArn"]),
                    "copy": dct["PolicyArn"],
                },
            )
            for dct in res.get("AttachedPolicies", [])
        ]

        res = ars.bsm.iam_client.list_role_policies(RoleName=self.name, MaxItems=50)
        inline_policy_items = [
            res_lib.DetailItem(
                title="<inline policy>: {}".format(policy_name),
                subtitle="🌐 Tap 'Enter' to open url (inline policy doesn't have ARN)",
                uid=f"policy {policy_name}",
                variables={
                    "url": ars.aws_console.iam.get_role_inline_policy(
                        role_name_or_arn=self.name,
                        policy_name=policy_name,
                    ),
                    "copy": arns.res.IamPolicy.new(
                        aws_account_id=ars.bsm.aws_account_id, name=policy_name
                    ).to_arn(),
                },
            )
            for policy_name in res.get("PolicyNames", [])
        ]

        res = ars.bsm.iam_client.list_role_tags(RoleName=self.name)
        tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("Tags", [])}
        tag_items = res_lib.DetailItem.from_tags(tags)

        return [
            res_lib.DetailItem(
                title=f"<arn>: {self.arn}",
                subtitle="📋 Tap 'Ctrl + A' to copy.",
                uid="Arn",
                variables={"copy": self.arn, "url": None},
            ),
            res_lib.DetailItem(
                title=f"<role_id>: {role_id}",
                subtitle="📋 Tap 'Ctrl + A' to copy.",
                uid="RoleId",
                variables={"copy": str(self.raw_data), "url": None},
            ),
            res_lib.DetailItem(
                title=f"<trust entities>: {assume_role_policy_document}",
                subtitle="📋 Tap 'Ctrl + A' to copy.",
                uid="AssumeRolePolicyDocument",
                variables={
                    "copy": json.dumps(assume_role_policy_document, indent=4),
                    "url": None,
                },
            ),
            *managed_policy_items,
            *inline_policy_items,
            *tag_items,
        ]


"""
https://us-east-1.console.aws.amazon.com/iamv2/home?region=eu-west-1#/roles/details/story-gesa-1045-athena-partitioner-role/editPolicy/story-gesa-1045-athena-partitioner-role-inline-policy?step=addPermissions
https://us-east-1.console.aws.amazon.com/iam/home#/policies/arn:aws:iam::414570653400:policy/story-gesa-1045-athena-partitioner-role-inline-policy$jsonEditor
"""
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


@dataclasses.dataclass
class IamPolicy(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    policy_arn: str = dataclasses.field()
    create_date: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["PolicyName"],
            name=resource["PolicyName"],
            policy_arn=resource["Arn"],
            create_date=extract_datetime(resource),
        )

    @property
    def title(self) -> str:
        return self.name

    @property
    def subtitle(self) -> str:
        return f"<create_at>: {self.create_date}, <arn>: {self.arn}"

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.policy_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_policy(name_or_arn=self.arn)


iam_policy_searcher = res_lib.Searcher(
    # list resources
    service="iam",
    method="list_policies",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Policies"),
    # extract document
    doc_class=IamPolicy,
    # search
    resource_type="iam-policy",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="policy_arn"),
        res_lib.sayt.StoredField(name="create_date"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value

if T.TYPE_CHECKING:
    from ..ars import ARS


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
        return format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            format_key_value("create_at", self.create_date),
            format_key_value("arn", self.arn),
            self.short_subtitle,
        )

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
        return format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            format_key_value("create_at", self.create_date),
            format_key_value("arn", self.arn),
            self.short_subtitle,
        )

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
            return format_key_value("🪖 name", self.name)
        else:
            return format_key_value("🧢 name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            format_key_value("create_at", self.create_date),
            format_key_value("arn", self.arn),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.role_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_role(name_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        detail_items.extend([
            Item("role_id", self.raw_data["RoleId"]),
            Item("trust_entities", self.one_line(self.raw_data["AssumeRolePolicyDocument"])),
        ])

        with self.enrich_details(detail_items):
            res = ars.bsm.iam_client.list_attached_role_policies(
                RoleName=self.name, MaxItems=50,
            )
            detail_items.extend([
                Item(
                    "managed policy",
                    dct["PolicyArn"],
                    dct["PolicyName"],
                    ars.aws_console.iam.get_policy(name_or_arn=dct["PolicyArn"]),
                )
                for dct in res.get("AttachedPolicies", [])
            ])

        with self.enrich_details(detail_items):
            res = ars.bsm.iam_client.list_role_policies(RoleName=self.name, MaxItems=50)
            detail_items.extend([
                Item(
                    name="inline policy",
                    value=arns.res.IamPolicy.new(
                        aws_account_id=ars.bsm.aws_account_id,
                        name=policy_name,
                    ).to_arn(),
                    text=policy_name,
                    url=ars.aws_console.iam.get_role_inline_policy(
                        role_name_or_arn=self.name,
                        policy_name=policy_name,
                    ),
                )
                for policy_name in res.get("PolicyNames", [])
            ])

        with self.enrich_details(detail_items):
            res = ars.bsm.iam_client.list_role_tags(RoleName=self.name)
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items
    # fmt: on


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
        return format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            format_key_value("create_at", self.create_date),
            format_key_value("arn", self.arn),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.policy_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_policy(name_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        detail_items.append(Item("create_date", self.create_date))

        with self.enrich_details(detail_items):
            res = ars.bsm.iam_client.get_policy(PolicyArn=self.arn)
            dct = res["Policy"]
            policy_id = dct["PolicyId"]
            default_version_id = dct["DefaultVersionId"]
            attachment_count = dct["AttachmentCount"]
            description = dct.get("Description", "No description")
            res = ars.bsm.iam_client.get_policy_version(PolicyArn=self.arn, VersionId=default_version_id)
            document: dict = res["PolicyVersion"]["Document"]
            detail_items.extend([
                Item("policy_id", policy_id),
                Item("default_version_id", default_version_id),
                Item("attachment_count", attachment_count),
                Item("description", description),
                Item("document", self.one_line(document)),
            ])

        with self.enrich_details(detail_items):
            res = ars.bsm.iam_client.list_policy_tags(PolicyArn=self.arn)
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items
    # fmt: on


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

# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


class IamMixin:
    @property
    def create_date(self: rl.ResourceDocument) -> str:
        return rl.get_datetime_simple_fmt(self.raw_data, "CreateDate")

    @property
    def arn(self: rl.ResourceDocument) -> str:
        return self.raw_data["Arn"]


@dataclasses.dataclass
class IamGroup(IamMixin, rl.ResourceDocument):
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["GroupName"],
            name=resource["GroupName"],
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            rl.format_key_value("create_at", self.create_date),
            rl.format_key_value("arn", self.arn),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.iam.get_user_group(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.iam.groups


class IamGroupSearcher(rl.BaseSearcher[IamGroup]):
    pass


iam_group_searcher = IamGroupSearcher(
    # list resources
    service="iam",
    method="list_groups",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("Groups"),
    # extract document
    doc_class=IamGroup,
    # search
    resource_type=rl.SearcherEnum.iam_group.value,
    fields=IamGroup.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.iam_group.value),
    more_cache_key=None,
)


@dataclasses.dataclass
class IamUser(IamMixin, rl.ResourceDocument):
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["UserName"],
            name=resource["UserName"],
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            rl.format_key_value("create_at", self.create_date),
            rl.format_key_value("arn", self.arn),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.iam.get_user(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.iam.users


class IamUserSearcher(rl.BaseSearcher[IamUser]):
    pass


iam_user_searcher = IamUserSearcher(
    # list resources
    service="iam",
    method="list_users",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("Users"),
    # extract document
    doc_class=IamUser,
    # search
    resource_type=rl.SearcherEnum.iam_user.value,
    fields=IamUser.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.iam_user.value),
    more_cache_key=None,
)


@dataclasses.dataclass
class IamRole(IamMixin, rl.ResourceDocument):
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["RoleName"],
            name=resource["RoleName"],
        )

    def is_service_role(self) -> bool:
        return "/aws-service-role/" in self.arn

    @property
    def title(self) -> str:
        if self.is_service_role():
            return rl.format_key_value("🪖 name", self.name)
        else:
            return rl.format_key_value("🧢 name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            rl.format_key_value("create_at", self.create_date),
            rl.format_key_value("arn", self.arn),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.iam.get_role(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.iam.roles

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        trust_entities = self.raw_data["AssumeRolePolicyDocument"]
        detail_items.extend(
            [
                from_detail("role_id", self.raw_data["RoleId"], url=url),
                from_detail(
                    "trust_entities",
                    trust_entities,
                    self.one_line(trust_entities),
                    url=url,
                ),
            ]
        )

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.iam_client.list_attached_role_policies(
                RoleName=self.name,
                MaxItems=50,
            )
            detail_items.extend([
                from_detail(
                    key="managed policy",
                    value=dct["PolicyArn"],
                    value_text=dct["PolicyName"],
                    url=ars.aws_console.iam.get_policy(name_or_arn=dct["PolicyArn"]),
                )
                for dct in res.get("AttachedPolicies", [])
            ])

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.iam_client.list_role_policies(RoleName=self.name, MaxItems=50)
            detail_items.extend(
                [
                    from_detail(
                        key="inline policy",
                        value=arns.res.IamPolicy.new(
                            aws_account_id=ars.bsm.aws_account_id,
                            name=policy_name,
                        ).to_arn(),
                        value_text=policy_name,
                        url=ars.aws_console.iam.get_role_inline_policy(
                            role_name_or_arn=self.name,
                            policy_name=policy_name,
                        ),
                    )
                    for policy_name in res.get("PolicyNames", [])
                ]
            )

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.iam_client.list_role_tags(RoleName=self.name)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class IamRoleSearcher(rl.BaseSearcher[IamRole]):
    pass


iam_role_searcher = IamRoleSearcher(
    # list resources
    service="iam",
    method="list_roles",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("Roles"),
    # extract document
    doc_class=IamRole,
    # search
    resource_type=rl.SearcherEnum.iam_role.value,
    fields=IamRole.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.iam_role.value),
    more_cache_key=None,
)


@dataclasses.dataclass
class IamPolicy(IamMixin, rl.ResourceDocument):
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["PolicyName"],
            name=resource["PolicyName"],
        )

    @property
    def title(self) -> str:
        return rl.format_key_value("name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            rl.format_key_value("create_at", self.create_date),
            rl.format_key_value("arn", self.arn),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.iam.get_policy(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.iam.policies

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)
        detail_items.append(from_detail("create_date", self.create_date))
        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.iam_client.get_policy(PolicyArn=self.arn)
            dct = res["Policy"]
            policy_id = dct["PolicyId"]
            default_version_id = dct["DefaultVersionId"]
            attachment_count = dct["AttachmentCount"]
            description = dct.get("Description", "No description")
            res = ars.bsm.iam_client.get_policy_version(PolicyArn=self.arn, VersionId=default_version_id)
            document: dict = res["PolicyVersion"]["Document"]
            detail_items.extend([
                from_detail("policy_id", policy_id, url=url),
                from_detail("default_version_id", default_version_id, url=url),
                from_detail("attachment_count", attachment_count, url=url),
                from_detail("description", description, url=url),
                from_detail("document", document, self.one_line(document), url=url),
            ])
        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.iam_client.list_policy_tags(PolicyArn=self.arn)
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("Tags", [])}
            detail_items.extend(rl.DetailItem.from_tags(tags, url))
        return detail_items
    # fmt: on


class IamPolicySearcher(rl.BaseSearcher[IamPolicy]):
    pass


iam_policy_searcher = IamPolicySearcher(
    # list resources
    service="iam",
    method="list_policies",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("Policies"),
    # extract document
    doc_class=IamPolicy,
    # search
    resource_type=rl.SearcherEnum.iam_policy.value,
    fields=IamPolicy.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.iam_policy.value),
    more_cache_key=None,
)

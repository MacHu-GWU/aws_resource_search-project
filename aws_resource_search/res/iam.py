# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


def extract_datetime(resource: res_lib.T_RESULT_DATA) -> str:
    return res_lib.get_datetime_isofmt(resource, "CreateDate", "No CreateDate")


class IamMixin:
    @property
    def create_date(self: res_lib.BaseDocument) -> str:
        return res_lib.get_datetime_simplefmt(self.raw_data, "CreateDate")

    @property
    def arn(self: res_lib.BaseDocument) -> str:
        return self.raw_data["Arn"]


@dataclasses.dataclass
class IamGroup(IamMixin, res_lib.BaseDocument):
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["GroupName"],
            name=resource["GroupName"],
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

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_user_group(name_or_arn=self.arn)


class IamGroupSearcher(res_lib.Searcher[IamGroup]):
    pass


iam_group_searcher = IamGroupSearcher(
    # list resources
    service="iam",
    method="list_groups",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Groups"),
    # extract document
    doc_class=IamGroup,
    # search
    resource_type=SearcherEnum.iam_group,
    fields=res_lib.define_fields(),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class IamUser(IamMixin, res_lib.BaseDocument):
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["UserName"],
            name=resource["UserName"],
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

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_user(name_or_arn=self.arn)


class IamUserSearcher(res_lib.Searcher[IamUser]):
    pass


iam_user_searcher = IamUserSearcher(
    # list resources
    service="iam",
    method="list_users",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Users"),
    # extract document
    doc_class=IamUser,
    # search
    resource_type=SearcherEnum.iam_user,
    fields=res_lib.define_fields(),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class IamRole(IamMixin, res_lib.BaseDocument):
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

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_role(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

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

        with self.enrich_details(detail_items):
            res = ars.bsm.iam_client.list_attached_role_policies(
                RoleName=self.name,
                MaxItems=50,
            )
            # fmt: off
            detail_items.extend([
                from_detail(
                    name="managed policy",
                    value=dct["PolicyArn"],
                    text=dct["PolicyName"],
                    url=ars.aws_console.iam.get_policy(name_or_arn=dct["PolicyArn"]),
                )
                for dct in res.get("AttachedPolicies", [])
            ])
            # fmt: on

        with self.enrich_details(detail_items):
            res = ars.bsm.iam_client.list_role_policies(RoleName=self.name, MaxItems=50)
            detail_items.extend(
                [
                    from_detail(
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
                ]
            )

        with self.enrich_details(detail_items):
            res = ars.bsm.iam_client.list_role_tags(RoleName=self.name)
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

        return detail_items


class IamRoleSearcher(res_lib.Searcher[IamRole]):
    pass


iam_role_searcher = IamRoleSearcher(
    # list resources
    service="iam",
    method="list_roles",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Roles"),
    # extract document
    doc_class=IamRole,
    # search
    resource_type=SearcherEnum.iam_role,
    fields=res_lib.define_fields(),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class IamPolicy(IamMixin, res_lib.BaseDocument):
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["PolicyName"],
            name=resource["PolicyName"],
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

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.iam.get_policy(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        detail_items.append(from_detail("create_date", self.create_date))
        # fmt: off
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
                from_detail("policy_id", policy_id, url=url),
                from_detail("default_version_id", default_version_id, url=url),
                from_detail("attachment_count", attachment_count, url=url),
                from_detail("description", description, url=url),
                from_detail("document", document, self.one_line(document), url=url),
            ])
        # fmt: on
        with self.enrich_details(detail_items):
            res = ars.bsm.iam_client.list_policy_tags(PolicyArn=self.arn)
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))
        return detail_items


class IamPolicySearcher(res_lib.Searcher[IamPolicy]):
    pass


iam_policy_searcher = IamPolicySearcher(
    # list resources
    service="iam",
    method="list_policies",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Policies"),
    # extract document
    doc_class=IamPolicy,
    # search
    resource_type=SearcherEnum.iam_policy,
    fields=res_lib.define_fields(),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

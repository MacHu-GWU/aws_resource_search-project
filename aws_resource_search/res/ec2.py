# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value, highlight_text

if T.TYPE_CHECKING:
    from ..ars import ARS


ec2_instance_state_icon_mapper = {
    "pending": "🟡",
    "running": "🟢",
    "shutting-down": "🟤",
    "terminated": "⚫",
    "stopping": "🟠",
    "stopped": "🔴️",
}


@dataclasses.dataclass
class Ec2Instance(res_lib.BaseDocument):
    state: str = dataclasses.field()
    inst_type: str = dataclasses.field()
    vpc_id: str = dataclasses.field()
    subnet_id: str = dataclasses.field()
    id: str = dataclasses.field()
    id_ng: str = dataclasses.field()
    name: str = dataclasses.field()
    inst_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        tags = {dct["Key"]: dct["Value"] for dct in resource.get("Tags", [])}
        return cls(
            raw_data=resource,
            state=resource["State"]["Name"],
            inst_type=resource["InstanceType"],
            vpc_id=resource.get("VpcId", "no vpc id"),
            subnet_id=resource.get("SubnetId", "no subnet id"),
            id=resource["InstanceId"],
            id_ng=resource["InstanceId"],
            name=tags.get("Name", "No instance name"),
            inst_arn=arns.res.Ec2Instance.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                resource_id=resource["InstanceId"],
            ).to_arn(),
        )

    @property
    def title(self) -> str:
        return format_key_value("name_tag", self.name)

    @property
    def subtitle(self) -> str:
        state_icon = ec2_instance_state_icon_mapper[self.state]
        return "{} | {} | {} | {}, {}".format(
            f"{state_icon} {self.state}",
            highlight_text(self.id),
            self.inst_type,
            f"vpc = {self.vpc_id}",
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.id

    @property
    def arn(self) -> str:
        return self.inst_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.ec2.get_instance(instance_id_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        inst_id = self.id
        inst_type = self.inst_type
        state = self.state
        vpc_id = self.vpc_id
        subnet_id = self.subnet_id
        public_ip = self.raw_data.get("PublicIpAddress", "NA")
        private_ip = self.raw_data.get("PrivateIpAddress", "NA")
        platform = self.raw_data.get("Platform", "NA")
        inst_profile = self.raw_data.get("IamInstanceProfile", {}).get("Arn", "NA")

        state_icon = ec2_instance_state_icon_mapper[state]
        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        detail_items = [
            Item("inst_id", inst_id, url=aws.ec2.get_instance(inst_id)),
            Item("inst_type", inst_type),
            Item("state", state, text=f"{state_icon} {state}"),
            Item("vpc_id", vpc_id, url=aws.vpc.get_vpc(vpc_id)),
            Item("subnet_id", subnet_id, url=aws.vpc.get_subnet(subnet_id)),
            Item("public_ip", public_ip),
            Item("private_ip", private_ip),
            Item("platform", platform),
            Item("inst_profile", inst_profile),
        ]

        detail_items.extend(
            [
                Item(
                    name="sg",
                    value=dct["GroupId"],
                    text="{} | {}".format(dct["GroupId"], dct["GroupName"]),
                    url=aws.vpc.get_security_group(dct["GroupId"]),
                    uid=dct["GroupId"],
                )
                for dct in self.raw_data.get("SecurityGroups", [])
            ]
        )

        tags: dict = {dct["Key"]: dct["Value"] for dct in self.raw_data.get("Tags", [])}
        detail_items.extend(res_lib.DetailItem.from_tags(tags))
        return detail_items


ec2_instance_searcher = res_lib.Searcher(
    # list resources
    service="ec2",
    method="describe_instances",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Reservations[].Instances[]"),
    # extract document
    doc_class=Ec2Instance,
    # search
    resource_type="ec2-instance",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.NgramWordsField(name="state", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="inst_type"),
        res_lib.sayt.NgramWordsField(name="vpc_id", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.NgramWordsField(
            name="subnet_id", minsize=2, maxsize=4, stored=True
        ),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="inst_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


ec2_vpc_state_icon_mapper = {
    "pending": "🟡",
    "available": "🟢",
}


@dataclasses.dataclass
class Ec2Vpc(res_lib.BaseDocument):
    is_default: bool = dataclasses.field()
    state: str = dataclasses.field()
    cidr_ipv4: str = dataclasses.field()
    cidr_ipv6: str = dataclasses.field()
    id: str = dataclasses.field()
    id_ng: str = dataclasses.field()
    name: str = dataclasses.field()
    vpc_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        tags = {dct["Key"]: dct["Value"] for dct in resource.get("Tags", [])}

        CidrBlockAssociationSet = resource.get("CidrBlockAssociationSet", [])
        if CidrBlockAssociationSet:
            cidr_ipv4 = CidrBlockAssociationSet[0].get("CidrBlock", "NA")
        else:
            cidr_ipv4 = "NA"

        Ipv6CidrBlockAssociationSet = resource.get("Ipv6CidrBlockAssociationSet", [])
        if Ipv6CidrBlockAssociationSet:
            cidr_ipv6 = Ipv6CidrBlockAssociationSet[0].get("Ipv6CidrBlock", "NA")
        else:
            cidr_ipv6 = "NA"

        return cls(
            raw_data=resource,
            is_default=resource["IsDefault"],
            state=resource["State"],
            cidr_ipv4=cidr_ipv4,
            cidr_ipv6=cidr_ipv6,
            id=resource["VpcId"],
            id_ng=resource["VpcId"],
            name=tags.get("Name", "No vpc name"),
            vpc_arn=arns.res.Vpc.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                resource_id=resource["VpcId"],
            ).to_arn(),
        )

    @property
    def title(self) -> str:
        return format_key_value("name_tag", self.name)

    @property
    def subtitle(self) -> str:
        state_icon = ec2_vpc_state_icon_mapper[self.state]
        return "{} | {} | {}, {}".format(
            f"{state_icon} {self.state}",
            highlight_text(self.id),
            format_key_value("is_default", self.is_default),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.id

    @property
    def arn(self) -> str:
        return self.vpc_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.vpc.get_vpc(vpc_id=self.id)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        state_icon = ec2_vpc_state_icon_mapper[self.state]
        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        detail_items = [
            Item("vpc_id", self.id, url=aws.vpc.get_vpc(self.id)),
            Item("is_default", self.is_default),
            Item("state", self.state, text=f"{state_icon} {self.state}"),
            Item("cidr_ipv4", self.cidr_ipv4),
            Item("cidr_ipv6", self.cidr_ipv6),
        ]

        tags: dict = {dct["Key"]: dct["Value"] for dct in self.raw_data.get("Tags", [])}
        detail_items.extend(res_lib.DetailItem.from_tags(tags))
        return detail_items


ec2_vpc_searcher = res_lib.Searcher(
    # list resources
    service="ec2",
    method="describe_vpcs",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Vpcs"),
    # extract document
    doc_class=Ec2Vpc,
    # search
    resource_type="ec2-vpc",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="is_default"),
        res_lib.sayt.NgramWordsField(name="state", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.NgramWordsField(
            name="cidr_ipv4", minsize=2, maxsize=3, stored=True
        ),
        res_lib.sayt.NgramWordsField(
            name="cidr_ipv6", minsize=2, maxsize=4, stored=True
        ),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="vpc_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class Ec2Subnet(res_lib.BaseDocument):
    state: str = dataclasses.field()
    vpc_id: str = dataclasses.field()
    az: str = dataclasses.field()
    id: str = dataclasses.field()
    id_ng: str = dataclasses.field()
    name: str = dataclasses.field()
    subnet_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        tags = {dct["Key"]: dct["Value"] for dct in resource.get("Tags", [])}
        return cls(
            raw_data=resource,
            state=resource["State"],
            vpc_id=resource["VpcId"],
            az=resource["AvailabilityZone"],
            id=resource["SubnetId"],
            id_ng=resource["SubnetId"],
            name=tags.get("Name", "No subnet name"),
            subnet_arn=resource["SubnetArn"],
        )

    @property
    def title(self) -> str:
        return format_key_value("name_tag", self.name)

    @property
    def subtitle(self) -> str:
        state_icon = ec2_vpc_state_icon_mapper[self.state]
        return "{} | {} | {} | {}, {}".format(
            f"{state_icon} {self.state}",
            self.vpc_id,
            highlight_text(self.id),
            self.az,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.id

    @property
    def arn(self) -> str:
        return self.subnet_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.vpc.get_subnet(subnet_id=self.id)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        state_icon = ec2_vpc_state_icon_mapper[self.state]
        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        detail_items = [
            Item("subnet_id", self.id, url=aws.vpc.get_subnet(self.id)),
            Item("vpc_id", self.vpc_id, url=aws.vpc.get_vpc(self.vpc_id)),
            Item("az", self.az),
            Item("state", self.state, text=f"{state_icon} {self.state}"),
            Item("available_ip", self.raw_data.get("AvailableIpAddressCount", "NA")),
            Item("enable_dns64", self.raw_data.get("EnableDns64", "NA")),
            Item("ipv6_native", self.raw_data.get("Ipv6Native", "NA")),
        ]

        tags: dict = {dct["Key"]: dct["Value"] for dct in self.raw_data.get("Tags", [])}
        detail_items.extend(res_lib.DetailItem.from_tags(tags))
        return detail_items


ec2_subnet_searcher = res_lib.Searcher(
    # list resources
    service="ec2",
    method="describe_subnets",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Subnets"),
    # extract document
    doc_class=Ec2Subnet,
    # search
    resource_type="ec2-subnet",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.NgramWordsField(name="state", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.NgramWordsField(name="vpc_id", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.NgramWordsField(name="az", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="subnet_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class Ec2SecurityGroup(res_lib.BaseDocument):
    description: str = dataclasses.field()
    vpc_id: str = dataclasses.field()
    id: str = dataclasses.field()
    id_ng: str = dataclasses.field()
    name: str = dataclasses.field()
    sg_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            description=resource.get("Description", "NA"),
            vpc_id=resource["VpcId"],
            id=resource["GroupId"],
            id_ng=resource["GroupId"],
            name=resource.get("GroupName", "NA"),
            sg_arn=arns.res.SecurityGroup.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                resource_id=resource["GroupId"],
            ).to_arn(),
        )

    @property
    def title(self) -> str:
        return format_key_value("name_tag", self.name)

    @property
    def subtitle(self) -> str:
        return "{} | {} | {}, {}".format(
            self.vpc_id,
            highlight_text(self.id),
            self.description,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.id

    @property
    def arn(self) -> str:
        return self.sg_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.vpc.get_security_group(sg_id=self.id)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        detail_items = [
            Item("sg_id", self.id, url=aws.vpc.get_security_group(self.id)),
            Item("description", self.description),
            Item("vpc_id", self.vpc_id, url=aws.vpc.get_vpc(self.vpc_id)),
        ]
        tags: dict = {dct["Key"]: dct["Value"] for dct in self.raw_data.get("Tags", [])}
        detail_items.extend(res_lib.DetailItem.from_tags(tags))
        return detail_items


ec2_securitygroup_searcher = res_lib.Searcher(
    # list resources
    service="ec2",
    method="describe_security_groups",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("SecurityGroups"),
    # extract document
    doc_class=Ec2SecurityGroup,
    # search
    resource_type="ec2-securitygroup",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.TextField(name="description", stored=True),
        res_lib.sayt.NgramWordsField(name="vpc_id", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="sg_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

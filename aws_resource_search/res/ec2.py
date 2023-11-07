# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import ShortcutEnum, format_key_value, highlight_text
from ..searchers_enum import SearcherEnum

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


class Ec2Mixin:
    @staticmethod
    def get_tags(raw_data) -> T.Dict[str, str]:
        return {dct["Key"]: dct["Value"] for dct in raw_data.get("Tags", [])}

    @property
    def tags(self: T.Union["Ec2Mixin", res_lib.BaseDocument]) -> T.Dict[str, str]:
        return self.get_tags(self.raw_data)


@dataclasses.dataclass
class Ec2Instance(res_lib.BaseDocument, Ec2Mixin):
    state: str = dataclasses.field()
    vpc_id: str = dataclasses.field()
    subnet_id: str = dataclasses.field()
    id_ng: str = dataclasses.field()
    inst_arn: str = dataclasses.field()

    @property
    def state_icon(self) -> str:
        return ec2_instance_state_icon_mapper[self.state]

    @property
    def inst_type(self) -> str:
        return self.raw_data["InstanceType"]

    @property
    def public_ip(self) -> str:
        return self.raw_data.get("PublicIpAddress", "NA")

    @property
    def private_ip(self) -> str:
        return self.raw_data.get("PrivateIpAddress", "NA")

    @property
    def platform(self) -> str:
        return self.raw_data.get("Platform", "NA")

    @property
    def inst_profile_arn(self) -> str:
        return self.raw_data.get("IamInstanceProfile", {}).get("Arn", "NA")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            state=resource["State"]["Name"],
            vpc_id=resource.get("VpcId", "no vpc id"),
            subnet_id=resource.get("SubnetId", "no subnet id"),
            id=resource["InstanceId"],
            id_ng=resource["InstanceId"],
            name=cls.get_tags(resource).get("Name", "No instance name"),
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
        return "{} | {} | {} | {}, {}".format(
            f"{self.state_icon} {self.state}",
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
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.ec2_client.describe_instances(InstanceIds=[self.id])
            instances = res.get("Reservations", [{}])[0].get("Instances", [])
            if len(instances) == 0:
                return [
                    res_lib.DetailItem.new(
                        title="🚨 EC2 instance not found, maybe it's deleted?",
                        subtitle=f"{ShortcutEnum.ENTER} to verify in AWS Console",
                        url=url,
                    )
                ]
            inst = self.from_resource(
                instances[0], ars.bsm, dict(InstanceIds=[self.id])
            )
            # fmt: off
            detail_items.extend([
                from_detail("inst_id", inst.id, url=url),
                from_detail("inst_type", inst.inst_type, url=url),
                from_detail("state", inst.state, f"{self.state_icon} {inst.state}", url=url),
                from_detail("vpc_id", inst.vpc_id, url=ars.aws_console.vpc.get_vpc(inst.vpc_id)),
                from_detail("subnet_id", inst.subnet_id, url=ars.aws_console.vpc.get_subnet(inst.subnet_id)),
                from_detail("public_ip", inst.public_ip, url=url),
                from_detail("private_ip", inst.private_ip, url=url),
                from_detail("platform", inst.platform, url=url),
                from_detail("inst_profile", inst.inst_profile_arn, url=ars.aws_console.iam.get_role(inst.inst_profile_arn.split("/")[-1])),
            ])
            # fmt: on
            detail_items.extend(
                [
                    from_detail(
                        name="sg",
                        value=dct["GroupId"],
                        text="{} | {}".format(dct["GroupId"], dct["GroupName"]),
                        url=ars.aws_console.vpc.get_security_group(dct["GroupId"]),
                        uid=dct["GroupId"],
                    )
                    for dct in self.raw_data.get("SecurityGroups", [])
                ]
            )
            detail_items.extend(res_lib.DetailItem.from_tags(self.tags, url=url))
        return detail_items


class Ec2InstanceSearcher(res_lib.Searcher[Ec2Instance]):
    pass


ec2_instance_searcher = Ec2InstanceSearcher(
    # list resources
    service="ec2",
    method="describe_instances",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Reservations[].Instances[]"),
    # extract document
    doc_class=Ec2Instance,
    # search
    resource_type=SearcherEnum.ec2_instance,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.NgramWordsField(name="state", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="vpc_id", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="subnet_id", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.StoredField(name="inst_arn"),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


ec2_vpc_state_icon_mapper = {
    "pending": "🟡",
    "available": "🟢",
}


@dataclasses.dataclass
class Ec2Vpc(res_lib.BaseDocument, Ec2Mixin):
    state: str = dataclasses.field()
    cidr_ipv4: str = dataclasses.field()
    cidr_ipv6: str = dataclasses.field()
    id_ng: str = dataclasses.field()
    vpc_arn: str = dataclasses.field()

    @property
    def is_default(self) -> str:
        return self.raw_data["IsDefault"]

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
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
            state=resource["State"],
            cidr_ipv4=cidr_ipv4,
            cidr_ipv6=cidr_ipv6,
            id=resource["VpcId"],
            id_ng=resource["VpcId"],
            name=cls.get_tags(resource).get("Name", "No vpc name"),
            vpc_arn=arns.res.Vpc.new(
                aws_account_id=bsm.aws_account_id,
                aws_region=bsm.aws_region,
                resource_id=resource["VpcId"],
            ).to_arn(),
        )

    @property
    def state_icon(self) -> str:
        return ec2_vpc_state_icon_mapper[self.state]

    @property
    def title(self) -> str:
        return format_key_value("name_tag", self.name)

    @property
    def subtitle(self) -> str:
        return "{} | {} | {}, {}".format(
            f"{self.state_icon} {self.state}",
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
        get_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.ec2_client.describe_vpcs(VpcIds=[self.id])
            vpcs = res.get("Vpcs", [])
            if len(vpcs) == 0:
                return [
                    res_lib.DetailItem.new(
                        title="🚨 Ec2 vpc not found, maybe it's deleted?",
                        subtitle=f"{ShortcutEnum.ENTER} to verify in AWS Console",
                        url=url,
                    )
                ]
            vpc = self.from_resource(vpcs[0], ars.bsm, dict(VpcIds=[self.id]))
            # fmt: off
            detail_items.extend(
                [
                    get_detail("vpc_id", vpc.id, url=url),
                    get_detail("is_default", vpc.is_default, url=url),
                    get_detail("state", vpc.state, f"{vpc.state_icon} {vpc.state}", url=url),
                    get_detail("cidr_ipv4", vpc.cidr_ipv4, url=url),
                    get_detail("cidr_ipv6", vpc.cidr_ipv6, url=url),
                ]
            )
            # fmt: on
            detail_items.extend(res_lib.DetailItem.from_tags(vpc.tags, url))
        return detail_items


class Ec2VpcSearcher(res_lib.Searcher[Ec2Vpc]):
    pass


ec2_vpc_searcher = Ec2VpcSearcher(
    # list resources
    service="ec2",
    method="describe_vpcs",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Vpcs"),
    # extract document
    doc_class=Ec2Vpc,
    # search
    resource_type=SearcherEnum.ec2_vpc,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.NgramWordsField(name="state", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="cidr_ipv4", minsize=2, maxsize=3, stored=True),
            res_lib.sayt.NgramWordsField(name="cidr_ipv6", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.StoredField(name="vpc_arn"),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class Ec2Subnet(res_lib.BaseDocument, Ec2Mixin):
    state: str = dataclasses.field()
    vpc_id: str = dataclasses.field()
    az: str = dataclasses.field()
    id_ng: str = dataclasses.field()

    @property
    def state_icon(self) -> str:
        return ec2_vpc_state_icon_mapper[self.state]

    @property
    def available_ip(self) -> str:
        return self.raw_data.get("AvailableIpAddressCount", "NA")

    @property
    def enable_dns64(self) -> str:
        return self.raw_data.get("EnableDns64", "NA")

    @property
    def ipv6_native(self) -> str:
        return self.raw_data.get("Ipv6Native", "NA")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            state=resource["State"],
            vpc_id=resource["VpcId"],
            az=resource["AvailabilityZone"],
            id=resource["SubnetId"],
            id_ng=resource["SubnetId"],
            name=cls.get_tags(resource).get("Name", "No subnet name"),
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
        return self.raw_data["SubnetArn"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.vpc.get_subnet(subnet_id=self.id)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)
        with self.enrich_details(detail_items):
            res = ars.bsm.ec2_client.describe_subnets(SubnetIds=[self.id])
            subnets = res.get("Subnets", [])
            if len(subnets) == 0:
                return [
                    res_lib.DetailItem.new(
                        title="🚨 EC2 subnet not found, maybe it's deleted?",
                        subtitle=f"{ShortcutEnum.ENTER} to verify in AWS Console",
                        url=url,
                    )
                ]
            subnet = self.from_resource(subnets[0], ars.bsm, dict(SubnetIds=[self.id]))
            # fmt: off
            detail_items.extend([
                from_detail("subnet_id", subnet.id, url=url),
                from_detail("vpc_id", subnet.vpc_id, url=ars.aws_console.vpc.get_vpc(subnet.vpc_id)),
                from_detail("az", subnet.az),
                from_detail("state", subnet.state, f"{subnet.state_icon} {subnet.state}", url=url),
                from_detail("available_ip", subnet.available_ip, url=url),
                from_detail("enable_dns64", subnet.enable_dns64, url=url),
                from_detail("ipv6_native", subnet.ipv6_native, url=url),
            ])
            # fmt: on
            detail_items.extend(res_lib.DetailItem.from_tags(subnet.tags, url))
        return detail_items


class Ec2SubnetSearcher(res_lib.Searcher[Ec2Subnet]):
    pass


ec2_subnet_searcher = Ec2SubnetSearcher(
    # list resources
    service="ec2",
    method="describe_subnets",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Subnets"),
    # extract document
    doc_class=Ec2Subnet,
    # search
    resource_type=SearcherEnum.ec2_subnet,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.NgramWordsField(name="state", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="vpc_id", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="az", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class Ec2SecurityGroup(res_lib.BaseDocument, Ec2Mixin):
    vpc_id: str = dataclasses.field()
    id_ng: str = dataclasses.field()
    sg_arn: str = dataclasses.field()

    @property
    def description(self) -> str:
        return res_lib.get_description(self.raw_data, "Description")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
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
        return format_key_value("group_name", self.name)

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
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)
        with self.enrich_details(detail_items):
            res = ars.bsm.ec2_client.describe_security_groups(GroupIds=[self.id])
            sgs = res.get("SecurityGroups", [])
            if len(sgs) == 0:
                return [
                    res_lib.DetailItem.new(
                        title="🚨 EC2 security group not found, maybe it's deleted?",
                        subtitle=f"{ShortcutEnum.ENTER} to verify in AWS Console",
                        url=url,
                    )
                ]
            sg = self.from_resource(sgs[0], ars.bsm, dict(GroupIds=[self.id]))
            # fmt: off
            detail_items.extend([
                from_detail("sg_id", sg.id, url=url),
                from_detail("description", sg.description, url=url),
                from_detail("vpc_id", sg.vpc_id, url=ars.aws_console.vpc.get_vpc(sg.vpc_id)),
            ])
            # fmt: on
            detail_items.extend(res_lib.DetailItem.from_tags(sg.tags, url))
        return detail_items


class Ec2SecurityGroupSearcher(res_lib.Searcher[Ec2SecurityGroup]):
    pass


ec2_securitygroup_searcher = Ec2SecurityGroupSearcher(
    # list resources
    service="ec2",
    method="describe_security_groups",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("SecurityGroups"),
    # extract document
    doc_class=Ec2SecurityGroup,
    # search
    resource_type=SearcherEnum.ec2_security_group,
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.NgramWordsField(name="vpc_id", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.StoredField(name="sg_arn"),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)
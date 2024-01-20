# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import sayt.api as sayt
import aws_arns.api as arns
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


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
    def tags(self: T.Union["Ec2Mixin", rl.ResourceDocument]) -> T.Dict[str, str]:
        return self.get_tags(self.raw_data)


@dataclasses.dataclass
class Ec2Instance(rl.ResourceDocument, Ec2Mixin):
    """
    todo: docstring
    """
    # fmt: off
    state: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="state", minsize=2, maxsize=4, stored=True)})
    vpc_id: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="vpc_id", minsize=2, maxsize=4, stored=True)})
    subnet_id: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="subnet_id", minsize=2, maxsize=4, stored=True)})
    id_ng: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True)})
    inst_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="inst_arn")})
    # fmt: on

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
        return rl.format_key_value("name_tag", self.name)

    @property
    def subtitle(self) -> str:
        return "{} | {} | {} | {}, {}".format(
            f"{self.state_icon} {self.state}",
            rl.highlight_text(self.id),
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

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.ec2.get_instance(instance_id_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.ec2.instances

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.ec2_client.describe_instances(InstanceIds=[self.id])
            instances = res.get("Reservations", [{}])[0].get("Instances", [])
            if len(instances) == 0:
                return [
                    rl.DetailItem.new(
                        title="🚨 EC2 instance not found, maybe it's deleted?",
                        subtitle=f"{rl.ShortcutEnum.ENTER} to verify in AWS Console",
                        url=url,
                    )
                ]
            inst = self.from_resource(
                instances[0], ars.bsm, dict(InstanceIds=[self.id])
            )
            detail_items.extend([
                from_detail("inst_id", inst.id, url=url),
                from_detail("inst_type", inst.inst_type, url=url),
                from_detail("state", inst.state, value_text=f"{self.state_icon} {inst.state}", url=url),
                from_detail("vpc_id", inst.vpc_id, url=ars.aws_console.vpc.get_vpc(inst.vpc_id)),
                from_detail("subnet_id", inst.subnet_id, url=ars.aws_console.vpc.get_subnet(inst.subnet_id)),
                from_detail("public_ip", inst.public_ip, url=url),
                from_detail("private_ip", inst.private_ip, url=url),
                from_detail("platform", inst.platform, url=url),
                from_detail("inst_profile", inst.inst_profile_arn, url=ars.aws_console.iam.get_role(inst.inst_profile_arn.split("/")[-1])),
            ])
            detail_items.extend(
                [
                    from_detail(
                        "sg",
                        dct["GroupId"],
                        value_text="{} | {}".format(dct["GroupId"], dct["GroupName"]),
                        url=ars.aws_console.vpc.get_security_group(dct["GroupId"]),
                        uid=dct["GroupId"],
                    )
                    for dct in inst.raw_data.get("SecurityGroups", [])
                ]
            )
            detail_items.extend(rl.DetailItem.from_tags(inst.tags, url=url))
        return detail_items
    # fmt: on


class Ec2InstanceSearcher(rl.BaseSearcher[Ec2Instance]):
    """
    todo: docstring
    """
    pass


ec2_instance_searcher = Ec2InstanceSearcher(
    # list resources
    service="ec2",
    method="describe_instances",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("Reservations[].Instances[]"),
    # extract document
    doc_class=Ec2Instance,
    # search
    resource_type=rl.SearcherEnum.ec2_instance.value,
    fields=Ec2Instance.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.ec2_instance.value),
    more_cache_key=None,
)


ec2_vpc_state_icon_mapper = {
    "pending": "🟡",
    "available": "🟢",
}


@dataclasses.dataclass
class Ec2Vpc(rl.ResourceDocument, Ec2Mixin):
    # fmt: off
    state: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="state", minsize=2, maxsize=4, stored=True)})
    cidr_ipv4: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="cidr_ipv4", minsize=2, maxsize=3, stored=True)})
    cidr_ipv6: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="cidr_ipv6", minsize=2, maxsize=4, stored=True)})
    id_ng: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True)})
    vpc_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="vpc_arn")})
    # fmt: on

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
        return rl.format_key_value("name_tag", self.name)

    @property
    def subtitle(self) -> str:
        return "{} | {} | {}, {}".format(
            f"{self.state_icon} {self.state}",
            rl.highlight_text(self.id),
            rl.format_key_value("is_default", self.is_default),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.id

    @property
    def arn(self) -> str:
        return self.vpc_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.vpc.get_vpc(vpc_id=self.id)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.vpc.vpcs

    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        get_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.ec2_client.describe_vpcs(VpcIds=[self.id])
            vpcs = res.get("Vpcs", [])
            if len(vpcs) == 0:
                return [
                    rl.DetailItem.new(
                        title="🚨 Ec2 vpc not found, maybe it's deleted?",
                        subtitle=f"{rl.ShortcutEnum.ENTER} to verify in AWS Console",
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
            detail_items.extend(rl.DetailItem.from_tags(vpc.tags, url))
        return detail_items


class Ec2VpcSearcher(rl.BaseSearcher[Ec2Vpc]):
    pass


ec2_vpc_searcher = Ec2VpcSearcher(
    # list resources
    service="ec2",
    method="describe_vpcs",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("Vpcs"),
    # extract document
    doc_class=Ec2Vpc,
    # search
    resource_type=rl.SearcherEnum.ec2_vpc.value,
    fields=Ec2Vpc.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.ec2_vpc.value),
    more_cache_key=None,
)


@dataclasses.dataclass
class Ec2Subnet(rl.ResourceDocument, Ec2Mixin):
    # fmt: off
    state: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="state", minsize=2, maxsize=4, stored=True)})
    vpc_id: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="vpc_id", minsize=2, maxsize=4, stored=True)})
    az: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="az", minsize=2, maxsize=4, stored=True)})
    id_ng: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True)})
    # fmt: on

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
        return rl.format_key_value("name_tag", self.name)

    @property
    def subtitle(self) -> str:
        state_icon = ec2_vpc_state_icon_mapper[self.state]
        return "{} | {} | {} | {}, {}".format(
            f"{state_icon} {self.state}",
            self.vpc_id,
            rl.highlight_text(self.id),
            self.az,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.id

    @property
    def arn(self) -> str:
        return self.raw_data["SubnetArn"]

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.vpc.get_subnet(subnet_id=self.id)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.vpc.subnets

    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.ec2_client.describe_subnets(SubnetIds=[self.id])
            subnets = res.get("Subnets", [])
            if len(subnets) == 0:
                return [
                    rl.DetailItem.new(
                        title="🚨 EC2 subnet not found, maybe it's deleted?",
                        subtitle=f"{rl.ShortcutEnum.ENTER} to verify in AWS Console",
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
            detail_items.extend(rl.DetailItem.from_tags(subnet.tags, url))
        return detail_items


class Ec2SubnetSearcher(rl.BaseSearcher[Ec2Subnet]):
    pass


ec2_subnet_searcher = Ec2SubnetSearcher(
    # list resources
    service="ec2",
    method="describe_subnets",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("Subnets"),
    # extract document
    doc_class=Ec2Subnet,
    # search
    resource_type=rl.SearcherEnum.ec2_subnet.value,
    fields=Ec2Subnet.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.ec2_subnet.value),
    more_cache_key=None,
)


@dataclasses.dataclass
class Ec2SecurityGroup(rl.ResourceDocument, Ec2Mixin):
    # fmt: off
    vpc_id: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="vpc_id", minsize=2, maxsize=4, stored=True)})
    id_ng: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True)})
    sg_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="sg_arn")})
    # fmt: on

    @property
    def description(self) -> str:
        return rl.get_description(self.raw_data, "Description")

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
        return rl.format_key_value("group_name", self.name)

    @property
    def subtitle(self) -> str:
        return "{} | {} | {}, {}".format(
            self.vpc_id,
            rl.highlight_text(self.id),
            self.description,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.id

    @property
    def arn(self) -> str:
        return self.sg_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.vpc.get_security_group(sg_id=self.id)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.vpc.security_groups

    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.ec2_client.describe_security_groups(GroupIds=[self.id])
            sgs = res.get("SecurityGroups", [])
            if len(sgs) == 0:
                return [
                    rl.DetailItem.new(
                        title="🚨 EC2 security group not found, maybe it's deleted?",
                        subtitle=f"{rl.ShortcutEnum.ENTER} to verify in AWS Console",
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
            detail_items.extend(rl.DetailItem.from_tags(sg.tags, url))
        return detail_items


class Ec2SecurityGroupSearcher(rl.BaseSearcher[Ec2SecurityGroup]):
    pass


ec2_securitygroup_searcher = Ec2SecurityGroupSearcher(
    # list resources
    service="ec2",
    method="describe_security_groups",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=rl.ResultPath("SecurityGroups"),
    # extract document
    doc_class=Ec2SecurityGroup,
    # search
    resource_type=rl.SearcherEnum.ec2_security_group.value,
    fields=Ec2SecurityGroup.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.ec2_security_group.value),
    more_cache_key=None,
)

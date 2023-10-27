# -*- coding: utf-8 -*-

import typing as T
import random

from .utils import guid, envs, rand_env

if T.TYPE_CHECKING:
    from .main import FakeAws


class VpcMixin:
    vpc_id_list: T.List[str] = list()
    subnet_id_list: T.List[str] = list()
    security_group_id_list: T.List[str] = list()

    @classmethod
    def create_vpc(cls: T.Type["FakeAws"]):
        for ith, env in enumerate(envs, start=1):
            kwargs = {
                "CidrBlock": f"10.{ith}.0.0/16",
                "TagSpecifications": [
                    dict(
                        ResourceType="vpc",
                        Tags=[dict(Key="Name", Value=f"{env}-{guid}-vpc")],
                    )
                ],
            }
            res = cls.bsm.ec2_client.create_vpc(**kwargs)
            vpc_id = res["Vpc"]["VpcId"]
            cls.vpc_id_list.append(vpc_id)

    @classmethod
    def create_subnet(
        cls: T.Type["FakeAws"],
        vpc_id_list: T.Optional[T.List[str]] = None,
    ):
        if vpc_id_list is None:
            vpc_id_list = cls.vpc_id_list
        for ith_vpc, vpc_id in enumerate(vpc_id_list, start=1):
            for ith_subnet, env in enumerate(envs, start=1):
                kwargs = {
                    "CidrBlock": f"10.{ith_vpc}.{ith_subnet}.0/24",
                    "TagSpecifications": [
                        dict(
                            ResourceType="subnet",
                            Tags=[
                                dict(Key="Name", Value=f"{vpc_id}/{env}-{guid}-subnet")
                            ],
                        )
                    ],
                }
                if vpc_id:
                    kwargs["VpcId"] = vpc_id
                res = cls.bsm.ec2_client.create_subnet(**kwargs)
                subnet_id = res["Subnet"]["SubnetId"]
                cls.subnet_id_list.append(subnet_id)

    @classmethod
    def create_security_group(
        cls: T.Type["FakeAws"],
        vpc_id_list: T.Optional[T.List[str]] = None,
    ):
        if vpc_id_list is None:
            vpc_id_list = cls.vpc_id_list
        # create some security group for default vpc and our manually created vpc
        for vpc_id in (None, *vpc_id_list):
            for ith, env in enumerate(envs, start=1):
                kwargs = {
                    "GroupName": f"{env}-{guid}-security-group",
                    "Description": "fake security group",
                    "TagSpecifications": [
                        dict(
                            ResourceType="security-group",
                            Tags=[
                                dict(
                                    Key="Name",
                                    Value=f"{vpc_id}/{env}-{guid}-security-group",
                                )
                            ],
                        )
                    ],
                }
                if vpc_id:
                    kwargs["VpcId"] = vpc_id
                res = cls.bsm.ec2_client.create_security_group(**kwargs)
                sg_id = res["GroupId"]
                cls.security_group_id_list.append(sg_id)

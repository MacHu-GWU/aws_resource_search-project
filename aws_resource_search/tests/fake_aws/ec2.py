# -*- coding: utf-8 -*-

import typing as T
import random

from .utils import guid, envs, rand_env

if T.TYPE_CHECKING:
    from .main import FakeAws


class Ec2Mixin:
    ec2_inst_id_list: T.List[str] = list()

    @classmethod
    def create_ec2_instances(cls: T.Type["FakeAws"]):
        image_id = cls.bsm.ec2_client.describe_images()["Images"][0]["ImageId"]

        for ith in range(1, 1 + 10):
            kwargs = dict(
                MinCount=1,
                MaxCount=1,
                ImageId=image_id,
            )
            if random.randint(1, 100) <= 70:
                env = rand_env()
                name = f"{env}-{guid}-{ith}-ec2-instance"
                kwargs["TagSpecifications"] = [
                    dict(
                        ResourceType="instance",
                        Tags=[dict(Key="Name", Value=name)],
                    )
                ]
            res = cls.bsm.ec2_client.run_instances(**kwargs)
            inst_id = res["Instances"][0]["InstanceId"]
            cls.ec2_inst_id_list.append(inst_id)

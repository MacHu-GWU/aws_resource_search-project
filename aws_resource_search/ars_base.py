# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses

import aws_console_url.api as aws_console_url

from .resource_searcher import ResourceSearcher, Request, Search
from .compat import cached_property
from .paths import path_data_json

if T.TYPE_CHECKING:
    from boto_session_manager import BotoSesManager


@dataclasses.dataclass
class ARSBase:
    bsm: "BotoSesManager" = dataclasses.field()

    @cached_property
    def data(self):
        return json.loads(path_data_json.read_text())

    def _get_rs(self, service_id: str, resource_type: str):
        """
        Get :class:`~aws_resource_search.resource_searcher.ResourceSearcher`
        instance by ``service_id`` and ``resource_type``. It read the data
        and construct the instance from the data.
        """
        dct = self.data[service_id][resource_type]
        request_data = dct["request"]
        request_data["client"] = service_id
        search_data = dct["search"]
        rs = ResourceSearcher(
            bsm=self.bsm,
            aws_console=aws_console_url.AWSConsole(
                aws_account_id=self.bsm.aws_account_id,
                aws_region=self.bsm.aws_region,
                bsm=self.bsm,
            ),
            service_id=service_id,
            resource_type=resource_type,
            request=Request.from_dict(request_data),
            search=Search.from_dict(search_data),
        )
        return rs

    # @cached_property
    # def ec2_instance(self):
    #     return self._get(service_id="ec2", resource_type="instance")
    #
    # @cached_property
    # def s3_bucket(self):
    #     return self._get(service_id="s3", resource_type="bucket")
    #
    # @cached_property
    # def cloudformation_stack(self):
    #     return self._get(service_id="cloudformation", resource_type="stack")

    #
    # @cached_property
    # def ec2_instance(self):
    #     return ResourceSearcher(
    #         bsm=self.bsm,
    #         aws_console=self.bsm.aws_console,
    #         service_id="ec2",
    #         resource_type="instance",
    #     )
    #

# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from boto_session_manager import BotoSesManager
from aws_console_url import AWSConsole

from ..compat import cached_property


@dataclasses.dataclass
class Searcher:
    """
    Base class for all AWS Resource Searcher.
    """

    aws_access_key_id: T.Optional[str] = dataclasses.field(default=None)
    aws_secret_access_key: T.Optional[str] = dataclasses.field(default=None)
    aws_session_token: T.Optional[str] = dataclasses.field(default=None)
    region_name: T.Optional[str] = dataclasses.field(default=None)
    profile_name: T.Optional[str] = dataclasses.field(default=None)
    is_us_gov_cloud: T.Optional[bool] = dataclasses.field(default=False)

    @cached_property
    def bsm(self) -> BotoSesManager:
        return BotoSesManager(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.region_name,
            profile_name=self.profile_name,
        )

    @cached_property
    def aws_console(self) -> AWSConsole:
        return AWSConsole(
            aws_account_id=self.bsm.aws_account_id,
            aws_region=self.bsm.aws_region,
            is_us_gov_cloud=self.is_us_gov_cloud,
            bsm=self.bsm,
        )

    def _enrich_aws_account_and_region(self, res):
        """
        res is a ``aws_resource_search.model.BaseAwsResourceModel`` instance.
        """
        res.aws_account_id = self.bsm.aws_account_id
        res.aws_region = self.bsm.aws_region
        return res

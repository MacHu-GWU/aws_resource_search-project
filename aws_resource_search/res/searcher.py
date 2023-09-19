# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from boto_session_manager import BotoSesManager
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

    @cached_property
    def bsm(self) -> BotoSesManager:
        return BotoSesManager(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.region_name,
            profile_name=self.profile_name,
        )

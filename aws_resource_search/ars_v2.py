# -*- coding: utf-8 -*-

import dataclasses

from .ars_base_v2 import ARSBase
from .compat import cached_property
from .res_lib import Searcher


@dataclasses.dataclass
class ARS(ARSBase):  # pragma: no cover
    @cached_property
    def glue_table(self) -> Searcher:
        return self._get_searcher("glue-table")
    
    @cached_property
    def iam_role(self) -> Searcher:
        return self._get_searcher("iam-role")
    
    @cached_property
    def s3_bucket(self) -> Searcher:
        return self._get_searcher("s3-bucket")
    
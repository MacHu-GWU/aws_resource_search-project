# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from .ars_base import ARSBase
from .compat import cached_property

if T.TYPE_CHECKING:
    from .resource_searcher import ResourceSearcher


@dataclasses.dataclass
class ARS(ARSBase):
    @cached_property
    def cloudformation_stack(self) -> "ResourceSearcher":
        return self._get_rs(service_id="cloudformation", resource_type="stack")
    
    @cached_property
    def dynamodb_table(self) -> "ResourceSearcher":
        return self._get_rs(service_id="dynamodb", resource_type="table")
    
    @cached_property
    def ec2_instance(self) -> "ResourceSearcher":
        return self._get_rs(service_id="ec2", resource_type="instance")
    
    @cached_property
    def glue_database(self) -> "ResourceSearcher":
        return self._get_rs(service_id="glue", resource_type="database")
    
    @cached_property
    def glue_table(self) -> "ResourceSearcher":
        return self._get_rs(service_id="glue", resource_type="table")
    
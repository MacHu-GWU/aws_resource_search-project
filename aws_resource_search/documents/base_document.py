# -*- coding: utf-8 -*-

"""
todo: add docstring
"""

import typing as T
import dataclasses

from ..model import BaseModel


@dataclasses.dataclass
class BaseArsDocument(BaseModel):
    """ """


T_ARS_DOCUMENT = T.TypeVar("T_ARS_DOCUMENT", bound=BaseArsDocument)

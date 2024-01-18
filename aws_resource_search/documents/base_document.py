# -*- coding: utf-8 -*-

"""
See :class:`BaseArsDocument`.
"""

import typing as T
import dataclasses

from ..base_model import BaseModel


@dataclasses.dataclass
class BaseArsDocument(BaseModel):
    """
    """


T_ARS_DOCUMENT = T.TypeVar("T_ARS_DOCUMENT", bound=BaseArsDocument)

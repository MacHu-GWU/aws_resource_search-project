# -*- coding: utf-8 -*-

"""
See :class:`InfoItem`.
"""

import dataclasses

from .base_item import BaseArsItem


@dataclasses.dataclass
class InfoItem(BaseArsItem): # pragma: no cover
    """
    Represent an item to show any information. Nothing would happen when user
    press any of the user action key. This is usually used to show some helpful
    information to suggest user what to do.
    """

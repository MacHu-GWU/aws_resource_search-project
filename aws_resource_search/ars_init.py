# -*- coding: utf-8 -*-

"""
This module manages the singleton object ``ars`` which holds all context data
such as boto session. It also the entry point to access the aws resource search
functionality.
"""

from .ars_def import ARS

ars = ARS.from_profile()
bsm = ars.bsm

# -*- coding: utf-8 -*-

"""
This module manages the singleton object ``ars`` which holds all context data
such as boto session. It also the entry point to access the aws resource search
functionality.
"""

import aws_console_url.api as aws_console_url
from boto_session_manager import BotoSesManager

from .ars_def import ARS

bsm = BotoSesManager()
ars = ARS(bsm=bsm, aws_console=aws_console_url.AWSConsole.from_bsm(bsm))

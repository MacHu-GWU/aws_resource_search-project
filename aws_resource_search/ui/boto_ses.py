# -*- coding: utf-8 -*-

"""
This module manages the underlying boto3 session for the UI. It always uses
the default url. You could use the `awscli_mate <https://github.com/MacHu-GWU/awscli_mate-project>`_
tool to set any given profile as default.
"""

from boto_session_manager import BotoSesManager

from ..ars import ARS

bsm = BotoSesManager()
ars = ARS(bsm=bsm)

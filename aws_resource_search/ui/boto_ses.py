# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager

from ..ars_v2 import ARS

bsm = BotoSesManager()
ars = ARS(bsm=bsm)

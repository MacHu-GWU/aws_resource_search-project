# -*- coding: utf-8 -*-

import hashlib
import subprocess
from .vendor.os_platform import IS_WINDOWS


def get_md5_hash(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()

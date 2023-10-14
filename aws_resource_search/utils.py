# -*- coding: utf-8 -*-

import hashlib
import subprocess
from .vendor.os_platform import IS_WINDOWS


def get_md5_hash(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()


def open_url(url: str):
    if IS_WINDOWS:
        cmd = "start"
    else:
        cmd = "open"
    subprocess.call([cmd, url])

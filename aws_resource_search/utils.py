# -*- coding: utf-8 -*-

import hashlib


def get_md5_hash(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()

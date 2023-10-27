# -*- coding: utf-8 -*-

"""
Usage::

    from .utils import guid, envs, rand_env
"""

import random
import string
from faker import Faker

fake = Faker()

_charset = string.ascii_lowercase + string.digits
guid = "".join([random.choice(_charset) for i in range(4)])
envs = ["sbx", "tst", "prd"]


def rand_env() -> str:
    return random.choice(envs)

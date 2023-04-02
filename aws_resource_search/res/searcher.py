# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import boto3
from boto_session_manager import BotoSesManager
from ..compat import cached_property


@dataclasses.dataclass
class Searcher:
    pass
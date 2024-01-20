# -*- coding: utf-8 -*-

"""
This module is an import namespace for everything related to the search.
"""

from .terminal import terminal
from .terminal import format_shortcut
from .terminal import highlight_text
from .terminal import format_resource_type
from .terminal import format_key
from .terminal import format_value
from .terminal import format_key_value
from .terminal import ShortcutEnum
from .terminal import SUBTITLE
from .terminal import SHORT_SUBTITLE
from .searcher_enum import SearcherEnum
from .downloader import T_RESULT_DATA
from .downloader import ResourceIterproxy
from .downloader import ResultPath
from .downloader import list_resources
from .downloader import extract_tags
from .documents.api import BaseArsDocument
from .documents.api import T_ARS_DOCUMENT
from .documents.api import ResourceTypeDocument
from .documents.api import get_utc_now
from .documents.api import to_human_readable_elapsed
from .documents.api import to_utc_dt
from .documents.api import SIMPLE_DT_FMT
from .documents.api import to_simple_dt_fmt
from .documents.api import to_iso_dt_fmt
from .documents.api import get_none_or_default
from .documents.api import get_description
from .documents.api import get_datetime
from .documents.api import get_datetime_simple_fmt
from .documents.api import get_datetime_iso_fmt
from .documents.api import ResourceDocument
from .documents.api import T_ARS_RESOURCE_DOCUMENT
from .items.api import BaseArsItem
from .items.api import T_ARS_ITEM
from .items.api import DetailItem
from .items.api import ExceptionItem
from .items.api import FileItem
from .items.api import InfoItem
from .items.api import UrlItem
from .items.api import AwsResourceTypeItem
from .items.api import AwsResourceItem
from .items.api import SetAwsProfileItem
from .items.api import ShowAwsInfoItem
from .base_searcher import preprocess_query
from .base_searcher import BaseSearcher
from .base_searcher import T_SEARCHER
from .conf.init import config

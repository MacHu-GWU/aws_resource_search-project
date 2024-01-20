# -*- coding: utf-8 -*-

from .res_lib import format_shortcut
from .res_lib import highlight_text
from .res_lib import format_resource_type
from .res_lib import format_key
from .res_lib import format_value
from .res_lib import format_key_value
from .res_lib import ShortcutEnum
from .res_lib import SUBTITLE
from .res_lib import SHORT_SUBTITLE
from .res_lib import SearcherEnum
from .res_lib import T_RESULT_DATA
from .res_lib import ResourceIterproxy
from .res_lib import ResultPath
from .res_lib import list_resources
from .res_lib import extract_tags
from .res_lib import BaseArsDocument
from .res_lib import T_ARS_DOCUMENT
from .res_lib import ResourceTypeDocument
from .res_lib import get_utc_now
from .res_lib import to_human_readable_elapsed
from .res_lib import to_utc_dt
from .res_lib import SIMPLE_DT_FMT
from .res_lib import to_simple_dt_fmt
from .res_lib import to_iso_dt_fmt
from .res_lib import get_none_or_default
from .res_lib import get_description
from .res_lib import get_datetime
from .res_lib import get_datetime_simple_fmt
from .res_lib import get_datetime_iso_fmt
from .res_lib import ResourceDocument
from .res_lib import T_ARS_RESOURCE_DOCUMENT
from .res_lib import BaseArsItem
from .res_lib import T_ARS_ITEM
from .res_lib import DetailItem
from .res_lib import ExceptionItem
from .res_lib import FileItem
from .res_lib import InfoItem
from .res_lib import UrlItem
from .res_lib import AwsResourceTypeItem
from .res_lib import AwsResourceItem
from .res_lib import SetAwsProfileItem
from .res_lib import ShowAwsInfoItem
from .res_lib import preprocess_query
from .res_lib import BaseSearcher
from .res_lib import T_SEARCHER
from .res_lib import config

from .ars_def import ARS

from .handlers.api import search_aws_profile_handler
from .handlers.api import search_resource_type_handler
from .handlers.api import search_resource_handler
from .handlers.api import show_aws_info_handler

from .ui_def import UI
from .ui_def import handler

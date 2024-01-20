# -*- coding: utf-8 -*-

"""
See :class:`ARSBase`.
"""

import typing as T
import shutil
import dataclasses
from pathlib import Path

from diskcache import Cache
from boto_session_manager import BotoSesManager
from boto_session_manager.manager import NOTHING
import aws_console_url.api as acu

from .exc import MalformedBotoSessionError
from .paths import dir_index, dir_cache
from .searcher_finder import SearcherFinder, searcher_finder
from .ars_search_patterns import ArsSearchPatternsMixin
from .ars_mixin import ARSMixin

if T.TYPE_CHECKING:  # pragma: no cover
    from .res_lib import T_SEARCHER


def validate_bsm(bsm: "BotoSesManager"):
    """
    validate the boto session manager. It has to have ``sts.get_caller_identity()``
    permission because we need to get aws_account_id, and be able to get ``aws_region``.
    """
    try:
        _ = bsm.aws_account_id
    except Exception as e:  # pragma: no cover
        raise MalformedBotoSessionError(
            f"failed to use sts.get_caller_identity() to get AWS account id:, "
            f"please check your default AWS profile in ~/.aws/config and ~/.aws/credentials, "
            f"error: {e}"
        )

    try:
        _ = bsm.aws_region
    except Exception as e:  # pragma: no cover
        raise MalformedBotoSessionError(
            f"failed to get AWS region of your boto session, "
            f"please check your default AWS profile in ~/.aws/config and ~/.aws/credentials, "
            f"error: {e}"
        )


@dataclasses.dataclass
class ARS(
    ArsSearchPatternsMixin,
    ARSMixin,
):
    """
    This class stands for "AWS Resource Search Base", provides method
    to search AWS resources in Python.

    In order to enable auto-complete in IDE, we need to explicitly declare
    per-resource-type searcher method in this class. However, we don't want
    to maintain this wiring logics. Instead, we use Jinja template to generate,
    a code

    Usage::

        # import the singleton ARS object
        >>> from aws_resource_search.api import ars
        >>> ars.s3_bucket.search("my bucket")
        [
            {
                "id": "my-bucket",
                "name": "my-bucket",
                ...
            },
            {
                ...
            },
        ]

    This class is a singleton object that holds all context data such as
    ``boto_session_manager.BotoSesManager``, ``aws_console_url.api.AwsConsole``.
    """
    # fmt: off
    bsm: "BotoSesManager" = dataclasses.field()
    aws_console: "aws_console_url.AWSConsole" = dataclasses.field()
    searcher_finder: "SearcherFinder" = dataclasses.field(default_factory=lambda: searcher_finder)
    dir_index: Path = dataclasses.field(default=dir_index)
    dir_cache: Path = dataclasses.field(default=dir_cache)
    cache: Cache = dataclasses.field(default=None)
    # fmt: on

    def __post_init__(self):
        self.dir_index = Path(self.dir_index)
        if self.dir_cache is not None:  # pragma: no cover
            self.dir_cache = Path(self.dir_cache)
        if self.cache is None:
            self.cache = Cache(str(self.dir_cache), disk_pickle_protocol=5)
        else:  # pragma: no cover
            self.dir_cache = Path(self.cache.directory)

    @classmethod
    def from_profile(cls, profile: T.Optional[str] = NOTHING):
        """
        Create a new :class:`ARSBase` object by an AWS profile. If None, then
        use the default AWS profile.
        """
        bsm = BotoSesManager(profile_name=profile)
        return cls.from_bsm(bsm=bsm)

    @classmethod
    def from_bsm(cls, bsm: T.Optional["BotoSesManager"] = None):
        if bsm is None:
            bsm = BotoSesManager()
        return cls(bsm=bsm, aws_console=acu.AWSConsole.from_bsm(bsm))

    def get_searcher(self, resource_type: str) -> "T_SEARCHER":
        """
        Get corresponding :class:`aws_resource_search.res_lib.Searcher`
        object by resource type.
        """
        sr = searcher_finder.import_searcher(resource_type)
        sr.bsm = self.bsm
        return sr

    def clear_all_cache(self):
        """
        Clear all cache.
        """
        shutil.rmtree(self.dir_index, ignore_errors=True)
        shutil.rmtree(self.dir_cache, ignore_errors=True)

    def all_resource_types(self) -> T.List[str]:
        """
        Return all resource types.
        """
        return searcher_finder.all_resource_types()

    def is_valid_resource_type(self, resource_type: str) -> bool:
        """
        Check if the resource type is supported.
        """
        return searcher_finder.is_valid_resource_type(resource_type)

    def set_profile(self, profile: T.Optional[str] = NOTHING):
        """
        Set all boto session related attributes (``bsm``, ``aws_console``,
        ``search_patterns``) to use a new AWS profile.

        Logics:

        1. Update the singleton ``bsm`` object by reset its cache and use a new AWS profile.
        2. Update the ``aws_console`` object to use the new ``bsm``
        3. Since we updated the ``bsm``, we also need to reset the ``searcher_finder``
            cache to recreate all ``Searcher`` objects.
        """
        # reset boto_session_manager.BotoSesManager
        self.bsm.aws_access_key_id = NOTHING
        self.bsm.aws_secret_access_key = NOTHING
        self.bsm.aws_session_token = NOTHING
        self.bsm.region_name = NOTHING
        self.bsm.botocore_session = NOTHING
        self.bsm.profile_name = profile
        self.bsm.clear_cache()
        validate_bsm(self.bsm)

        # reset aws_console_url.AWSConsole
        self.aws_console = acu.AWSConsole.from_bsm(self.bsm)

        # reset searcher_finder.SearcherFinder
        self.searcher_finder.searcher_cache.clear()

        # reset ARS.search_patterns
        _ = self.search_patterns
        self._clear_search_patterns_cache()

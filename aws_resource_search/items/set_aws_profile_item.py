# -*- coding: utf-8 -*-

"""
See :class:`SetAwsProfileItem`.
"""

import typing as T
import dataclasses

import awscli_mate.api as awscli_mate
import aws_console_url.api as aws_console_url

from ..terminal import ShortcutEnum, format_key_value, highlight_text
from .base_item import BaseArsItem

if T.TYPE_CHECKING:  # pragma: no cover
    from ..ars_def import ARS
    from ..ui.main import UI


def set_profile_in_bsm(profile: str, ars: "ARS"):
    """
    Update the singleton ``bsm`` object by reset its cache and use a new AWS profile.
    Also update all of related cached objects in ``ars``.
    """
    ars.bsm.aws_access_key_id = None
    ars.bsm.aws_secret_access_key = None
    ars.bsm.aws_session_token = None
    ars.bsm.region_name = None
    ars.bsm.botocore_session = None
    ars.bsm.profile_name = profile
    ars.bsm.clear_cache()

    ars.aws_console = aws_console_url.AWSConsole.from_bsm(ars.bsm)
    ars.searcher_finder.searcher_cache.clear()


@dataclasses.dataclass
class SetAwsProfileItem(BaseArsItem):
    """
    Represent an item in the aws profile search result.
    """

    def enter_handler(self, ui: "UI"):  # pragma: no cover
        awscli_mate.AWSCliConfig().set_profile_as_default(profile=self.arg)
        set_profile_in_bsm(self.arg, ui.ars)

    def post_enter_handler(self, ui: "UI"):  # pragma: no cover
        """
        When exiting the switch profile session, recover the original query input.
        """
        ui.line_editor.clear_line()
        ui.line_editor.enter_text(self.autocomplete)

    @classmethod
    def from_profile_region(
        cls,
        profile: str,
        region: str,
        autocomplete: str,
    ):
        """
        Factory method for :class:`SetAwsProfileItem`.

        :param profile: aws profile name
        :param region: aws region
        :param autocomplete: the existing query input before "!@" to recover to.
        """
        return cls(
            title="📝 {} | {}".format(
                format_key_value("profile", profile), format_key_value("region", region)
            ),
            subtitle=f"Hit {ShortcutEnum.ENTER} to set {highlight_text(profile)} as the default profile.",
            uid=f"aws-profile-{profile}",
            arg=profile,
            autocomplete=autocomplete,
        )

    @classmethod
    def from_many_profile_region_pairs(
        cls,
        pairs: T.List[T.Tuple[str, str]],
        autocomplete: str,
    ):
        """
        Another factory method to create many :class:`SetAwsProfileItem` at once.
        """
        return [
            cls.from_profile_region(profile, region, autocomplete)
            for profile, region in pairs
        ]

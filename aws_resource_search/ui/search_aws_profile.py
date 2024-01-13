# -*- coding: utf-8 -*-

"""
This module defines the logic to switch between aws profile without leaving the app.
"""

import typing as T
import dataclasses

import awscli_mate.api as awscli_mate

from ..compat import TypedDict
from ..res_lib import ArsBaseItem
from ..terminal import ShortcutEnum, highlight_text
from .boto_ses import bsm

if T.TYPE_CHECKING:
    from .main import UI


def set_profile_in_bsm(profile: str):
    """
    Update the singleton ``bsm`` object by reset its cache and use a new AWS profile.
    """
    bsm.aws_access_key_id = None
    bsm.aws_secret_access_key = None
    bsm.aws_session_token = None
    bsm.region_name = None
    bsm.botocore_session = None
    bsm.profile_name = profile
    bsm.clear_cache()


class SetAwsProfileItemVariables(TypedDict):
    n_backspace: int


@dataclasses.dataclass
class SetAwsProfileItem(ArsBaseItem):
    """
    Represent an item in the aws profile search result.

    :param variables: in AwsResourceItem, the variable is a dictionary including
        the original document object (not dict).
    """

    @classmethod
    def from_profile_region(
        cls, profile: str, region: str, autocomplete: str, n_backspace: int
    ):
        return cls(
            title=f"📝 {profile} | {region}",
            subtitle=f"Hit {ShortcutEnum.ENTER} to set {highlight_text(profile)} as the default profile.",
            uid=profile,
            arg=profile,
            autocomplete=autocomplete,
            variables={
                "n_backspace": n_backspace,
            },
        )

    def enter_handler(self, ui: "UI"):
        awscli_mate.AWSCliConfig().set_profile_as_default(profile=self.arg)
        set_profile_in_bsm(self.arg)

    def post_enter_handler(self, ui: "UI"):
        """
        When exiting the switch profile session, recover the original query input.
        """
        ui.line_editor.press_end()
        ui.line_editor.press_backspace(n=self.variables["n_backspace"])


def search_aws_profile_and_return_items(
    query: str,
):
    pairs = awscli_mate.get_sorted_profile_region_pairs(query=query)
    return pairs


def search_aws_profile_handler(
    ui: "UI",
    line_input: str,
    query: str,
    skip_ui: bool = False,
) -> T.List[SetAwsProfileItem]:
    ui.render.prompt = f"(Query)"
    pairs = search_aws_profile_and_return_items(query=query)
    return [
        SetAwsProfileItem.from_profile_region(
            profile,
            region,
            autocomplete=line_input,
            n_backspace=len(query) + 2,  # 2 for "!@"
        )
        for profile, region in pairs
    ]

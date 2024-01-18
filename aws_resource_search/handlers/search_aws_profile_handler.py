# -*- coding: utf-8 -*-

"""
See :func:`search_aws_profile_handler`.
"""

import typing as T

import awscli_mate.api as awscli_mate

from .. import res_lib_v1 as rl

if T.TYPE_CHECKING:
    from ..ui_def import UI


def search_aws_profile_and_return_items(
    query: str,
):
    pairs = awscli_mate.get_sorted_profile_region_pairs(query=query)
    return pairs


def search_aws_profile_handler(
    ui: "UI",
    line_input: str,
    profile_query: str,
    skip_ui: bool = False,
) -> T.List[rl.SetAwsProfileItem]:
    """
    Search AWS CLI profile in ``~/.aws/config`` file, order by similarity to the query.
    This function will be triggered when user type ``!@`` without leaving the app.

    :param line_input: the original query input by user before the ``!@``.
    :param profile_query: aws profile query, the text after ``!@``.

    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    ui.render.prompt = f"(Query)"
    pairs = search_aws_profile_and_return_items(query=profile_query)
    return [
        rl.SetAwsProfileItem.from_profile_region(
            profile=profile,
            region=region,
            autocomplete=line_input,
        )
        for profile, region in pairs
    ]

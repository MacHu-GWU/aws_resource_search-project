# -*- coding: utf-8 -*-

"""
See :func:`search_aws_profile_handler`.
"""

import typing as T

import sayt.api as sayt
import awscli_mate.api as awscli_mate

from ..paths import dir_index, dir_cache, path_aws_config
from .. import res_lib as rl

if T.TYPE_CHECKING:  # pragma: no cover
    from ..ui_def import UI


def downloader() -> T.List[sayt.T_DOCUMENT]:
    pairs = awscli_mate.AWSCliConfig().extract_profile_and_region_pairs()
    return [
        {
            "profile": profile,
            "profile_ng": profile,
            "region_ng": region,
        }
        for profile, region in pairs
    ]


index_name = "aws-resource-search-aws-profiles"
aws_profile_dataset = sayt.DataSet(
    dir_index=dir_index,
    index_name=index_name,
    fields=[
        sayt.IdField(name="profile", stored=True),
        sayt.NgramWordsField(name="profile_ng", stored=True, minsize=2, maxsize=10),
        sayt.NgramWordsField(name="region_ng", stored=True, minsize=2, maxsize=10),
    ],
    dir_cache=dir_cache,
    cache_key=index_name,
    cache_tag=index_name,
    cache_expire=5 * 60,
    downloader=downloader,
)


def search_aws_profile_and_return_items(
    line_input: str,
    profile_query: str,
    refresh_data: bool = False,
) -> T.List[rl.SetAwsProfileItem]:
    docs = aws_profile_dataset.search(
        query=profile_query,
        limit=50,
        simple_response=True,
        refresh_data=refresh_data,
    )
    if len(docs):
        return rl.SetAwsProfileItem.from_many_profile_region_pairs(
            pairs=[(doc["profile_ng"], doc["region_ng"]) for doc in docs],
            autocomplete=line_input,
        )
    else:
        return [
            rl.FileItem.from_file(
                path_aws_config,
                title="❗ Cannot find any AWS profile in ~/.aws/config",
            )
        ]


def search_aws_profile_handler(
    ui: "UI",
    line_input: str,
    profile_query: str,
    skip_ui: bool = False,
) -> T.List[rl.SetAwsProfileItem]:  # pragma: no cover
    """
    Search AWS CLI profile in ``~/.aws/config`` file, order by similarity to the query.
    This function will be triggered when user type ``!@`` without leaving the app.

    :param line_input: the original query input by user before the ``!@``.
    :param profile_query: aws profile query, the text after ``!@``.

    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    if skip_ui is False:  # pragma: no cover
        ui.render.prompt = f"(AWS Profile Query)"
    return search_aws_profile_and_return_items(
        line_input=line_input,
        profile_query=rl.preprocess_query(profile_query),
    )

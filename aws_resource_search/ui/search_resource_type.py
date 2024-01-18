# -*- coding: utf-8 -*-

"""
This module implements the resource type search feature.
"""

import typing as T
import json
import dataclasses

import sayt.api as sayt

from ..paths import dir_index, dir_cache, path_searchers_json
from .. import res_lib_v1 as rl

# from ..terminal import ShortcutEnum, format_resource_type
# from ..compat import TypedDict
# from ..res_lib import T_DOCUMENT_OBJ, preprocess_query, ArsBaseItem, OpenUrlItem

if T.TYPE_CHECKING:
    from .main import UI


def downloader() -> T.List[sayt.T_DOCUMENT]:
    data = json.loads(path_searchers_json.read_text())
    return [
        rl.ResourceTypeDocument(
            id=resource_type,
            name=resource_type,
            desc=dct["desc"],
            ngram=dct["ngram"],
        ).to_dict()
        for resource_type, dct in data.items()
    ]


index_name = "aws-resource-search-resource-types"
resource_type_dataset = sayt.DataSet(
    dir_index=dir_index,
    index_name=index_name,
    fields=[
        sayt.IdField(name="id", stored=True),
        sayt.NgramWordsField(name="name", stored=True, minsize=2, maxsize=10),
        sayt.StoredField(name="desc"),
        sayt.NgramWordsField(name="ngram", stored=True, minsize=2, maxsize=10),
    ],
    dir_cache=dir_cache,
    cache_key=index_name,
    cache_tag=index_name,
    cache_expire=24 * 60 * 60,
    downloader=downloader,
)


def search_resource_type_and_return_items(
    ui: "UI",
    query: str,
    refresh_data: bool = False,
) -> T.List[T.Union[rl.AwsResourceTypeItem, rl.UrlItem]]:
    """
    Search AWS Resource Type based on the query and return items.
    """
    docs = resource_type_dataset.search(
        query=query,
        limit=50,
        simple_response=True,
        refresh_data=refresh_data,
    )
    if len(docs):
        return rl.AwsResourceTypeItem.from_many_document(docs, ui.ars)
    else:
        return [
            rl.UrlItem.from_url(
                url="https://github.com/MacHu-GWU/aws_resource_search-project/issues/new?assignees=MacHu-GWU&labels=enhancement&projects=&template=support-new-aws-resource.md&title=%5BFeature%5D+I+want+to+be+able+to+search+%24%7Bservice_name%7D-%24%7Bresource_name%7D",
                title=f"🔴 No resource type found, maybe it is not supported yet.",
                subtitle=(
                    "Please try another query, "
                    "or type {} to submit a Github issue for new resource, "
                    "or tap {} to clear existing query."
                ).format(
                    rl.ShortcutEnum.ENTER,
                    rl.ShortcutEnum.TAB,
                ),
                autocomplete="",
            )
        ]


def select_resource_type_handler(
    ui: "UI",
    query: str,
    skip_ui: bool = False,
) -> T.List[T.Union[rl.AwsResourceTypeItem, rl.UrlItem]]:
    """
    **IMPORTANT** This handle filter resource types by query.

    :param query: service id and resource type search query input. For example:
        "s3 bucket", "ec2 inst"
    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    if skip_ui is False:
        ui.render.prompt = "(Resource Type)"
    final_query = rl.preprocess_query(query)

    # manually refresh data
    # show "loading" message
    if query.strip().endswith("!~"):
        if skip_ui is False:
            ui.run_handler(items=[])
            ui.repaint()
            ui.line_editor.press_backspace(n=2)
        return search_resource_type_and_return_items(
            ui=ui,
            query=rl.preprocess_query(final_query[:-2]),
            refresh_data=True,
        )

    # example: "ec2 inst"
    return search_resource_type_and_return_items(
        ui=ui,
        query=final_query,
        refresh_data=False,
    )

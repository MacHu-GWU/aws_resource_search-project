# -*- coding: utf-8 -*-

"""
This module implements the resource type search feature.
"""

import typing as T
import dataclasses

import sayt.api as sayt

from ..terminal import ShortcutEnum, highlight_text
from ..paths import dir_index, dir_cache
from ..searchers import searchers_metadata
from ..res_lib import preprocess_query, ArsBaseItem

if T.TYPE_CHECKING:
    from .main import UI


class ResourceTypeDocument(T.TypedDict):
    id: str
    name: str


def downloader():
    return [
        {"id": resource_type, "name": resource_type}
        for resource_type in searchers_metadata
    ]


index_name = "aws-resource-search-resource-types"
resource_type_dataset = sayt.DataSet(
    dir_index=dir_index,
    index_name=index_name,
    fields=[
        sayt.IdField(
            name="id",
            stored=True,
        ),
        sayt.NgramWordsField(
            name="name",
            stored=True,
            minsize=2,
            maxsize=6,
        ),
    ],
    dir_cache=dir_cache,
    cache_key=index_name,
    cache_tag=index_name,
    cache_expire=24 * 60 * 60,
    downloader=downloader,
)


@dataclasses.dataclass
class AwsResourceTypeItem(ArsBaseItem):
    """
    Represent an item in the resource type search result.
    """

    @classmethod
    def from_document(cls, doc: ResourceTypeDocument):
        """
        For example: if the doc is::

            {"id": "s3-bucket", "name": "s3-bucket"}

        Then the item will be::

            {
                "title": "s3-bucket",
                "subtitle": "hit 'Tab' and enter your query to search.",
                "uid": "s3-bucket",
                "arg": "s3-bucket",
                "autocomplete": "s3-bucket: ",
            }
        """
        resource_type = doc["name"]
        return cls(
            title=resource_type,
            subtitle=(
                f"hit {ShortcutEnum.TAB} and enter your query "
                f"to search {highlight_text(resource_type)}."
            ),
            uid=doc["id"],
            arg=doc["name"],
            autocomplete=doc["name"] + ": ",
        )

    @classmethod
    def from_many_document(cls, docs: T.Iterable[ResourceTypeDocument]):
        return [cls.from_document(doc) for doc in docs]


def search_resource_type_and_return_items(
    query: str,
    refresh_data: bool = False,
) -> T.List[AwsResourceTypeItem]:
    docs: T.List[ResourceTypeDocument] = resource_type_dataset.search(
        query=query,
        limit=50,
        simple_response=True,
        refresh_data=refresh_data,
    )
    return AwsResourceTypeItem.from_many_document(docs)


def select_resource_type_handler(
    ui: "UI",
    query: str,
) -> T.List[AwsResourceTypeItem]:
    """
    **IMPORTANT** This handle filter resource types by query.

    :param query: service id and resource type search query input. For example:
        "s3 bucket", "ec2 inst"
    """
    final_query = preprocess_query(query)

    # manually refresh data
    if query.strip().endswith("!~"):
        ui.run_handler(items=[])
        ui.repaint()
        ui.line_editor.press_backspace(n=2)
        return search_resource_type_and_return_items(
            query=preprocess_query(final_query[:-2]),
            refresh_data=True,
        )

    # example: "ec2 inst"
    return search_resource_type_and_return_items(query=final_query)

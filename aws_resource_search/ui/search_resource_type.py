# -*- coding: utf-8 -*-

"""
This module implements the resource type search feature.
"""

import typing as T
import json
import dataclasses

import sayt.api as sayt

from ..terminal import ShortcutEnum, format_resource_type
from ..paths import dir_index, dir_cache, path_searchers_json
from ..compat import TypedDict
from ..res_lib import T_DOCUMENT_OBJ, preprocess_query, ArsBaseItem, OpenUrlItem

if T.TYPE_CHECKING:
    from .main import UI


class ResourceTypeDocument(TypedDict):
    id: str
    name: str
    desc: str
    ngram: str


def downloader() -> T.List[ResourceTypeDocument]:
    data = json.loads(path_searchers_json.read_text())
    return [
        {
            "id": resource_type,
            "name": resource_type,
            "desc": dct["desc"],
            "ngram": dct["ngram"],
        }
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


class AwsResourceTypeItemVariables(TypedDict):
    """
    Type hint for the "variables" field in :class:`AwsResourceTypeItem`.
    """

    doc: ResourceTypeDocument
    resource_type: str


@dataclasses.dataclass
class AwsResourceTypeItem(ArsBaseItem):
    """
    Represent an item in the resource type search result.
    """
    variables: AwsResourceTypeItemVariables = dataclasses.field(default_factory=dict)

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
        desc = doc["desc"]
        return cls(
            title=f"{format_resource_type(resource_type)}: {desc}",
            subtitle=(
                f"hit {ShortcutEnum.TAB} or {ShortcutEnum.ENTER} and enter your query "
                f"to search {resource_type}."
            ),
            uid=doc["id"],
            arg=doc["name"],
            autocomplete=doc["name"] + ": ",
            variables={
                "doc": doc,
                "resource_type": resource_type,
            },
        )

    @classmethod
    def from_many_document(cls, docs: T.Iterable[ResourceTypeDocument]):
        return [cls.from_document(doc) for doc in docs]

    def enter_handler(self, ui: "UI"):
        """
        For resource type search, when user hit "Enter", it does the same thing
        as hitting "Tab" for auto-complete.
        """
        ui.line_editor.clear_line()
        if self.autocomplete:
            ui.line_editor.enter_text(self.autocomplete)

    def post_enter_handler(self, ui: "UI"):
        pass


def search_resource_type_and_return_items(
    query: str,
    refresh_data: bool = False,
) -> T.List[T.Union[AwsResourceTypeItem, OpenUrlItem]]:
    """
    Search AWS Resource Type based on the query and return items.
    """
    docs: T.List[ResourceTypeDocument] = resource_type_dataset.search(
        query=query,
        limit=50,
        simple_response=True,
        refresh_data=refresh_data,
    )
    if len(docs):
        return AwsResourceTypeItem.from_many_document(docs)
    else:
        return [
            OpenUrlItem(
                title=f"🔴 No resource type found, maybe it is not supported yet.",
                subtitle=(
                    "Please try another query, "
                    "or type {} to submit a Github issue for new resource, "
                    "or tap {} to clear existing query."
                ).format(
                    ShortcutEnum.ENTER,
                    ShortcutEnum.TAB,
                ),
                arg="https://github.com/MacHu-GWU/aws_resource_search-project/issues/new?assignees=MacHu-GWU&labels=enhancement&projects=&template=support-new-aws-resource.md&title=%5BFeature%5D+I+want+to+be+able+to+search+%24%7Bservice_name%7D-%24%7Bresource_name%7D",
                autocomplete="",
            )
        ]


def select_resource_type_handler(
    ui: "UI",
    query: str,
    skip_ui: bool = False,
) -> T.List[T.Union[AwsResourceTypeItem, OpenUrlItem]]:
    """
    **IMPORTANT** This handle filter resource types by query.

    :param query: service id and resource type search query input. For example:
        "s3 bucket", "ec2 inst"
    :param skip_ui: if True, skip the UI related logic, just return the items.
        this argument is used for third party integration.
    """
    if skip_ui is False:
        ui.render.prompt = "(Resource Type)"
    final_query = preprocess_query(query)

    # manually refresh data
    if query.strip().endswith("!~"):
        if skip_ui is False:
            ui.run_handler(items=[])
            ui.repaint()
            ui.line_editor.press_backspace(n=2)
        return search_resource_type_and_return_items(
            query=preprocess_query(final_query[:-2]),
            refresh_data=True,
        )

    # example: "ec2 inst"
    return search_resource_type_and_return_items(query=final_query)

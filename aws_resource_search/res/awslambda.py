# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from .. import res_lib
from ..terminal import format_key_value

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class LambdaFunction(res_lib.BaseDocument):
    description: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    func_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            description=resource.get("Description", "No Description"),
            id=resource["FunctionName"],
            name=resource["FunctionName"],
            func_arn=resource["FunctionArn"],
        )

    @property
    def title(self) -> str:
        return format_key_value("function_name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}".format(
            self.description,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.func_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.awslambda.get_function(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)

        with self.enrich_details(detail_items):
            res = ars.bsm.lambda_client.get_function(FunctionName=self.name)
            arn = res["Configuration"]["FunctionArn"]
            description = res["Configuration"].get("Description", "NA")
            role_arn = res["Configuration"]["Role"]
            runtime = res["Configuration"]["Runtime"]
            timeout = res["Configuration"]["Timeout"]
            memory_size = res["Configuration"]["MemorySize"]
            handler = res["Configuration"]["Handler"]
            state = res["Configuration"].get("State", "NA")
            last_modified = res["Configuration"]["LastModified"]

            detail_items.extend(
                [
                    Item("description", description),
                    Item(
                        "🧢 role_arn",
                        role_arn,
                        url=ars.aws_console.iam.get_role(role_arn),
                    ),
                    Item("runtime", runtime),
                    Item("timeout", timeout),
                    Item("memory_size", memory_size),
                    Item("handler", handler),
                    Item("state", state),
                    Item("last_modified", last_modified),
                ]
            )

            tags: dict = res.get("Tags", {})
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items


lambda_function_searcher = res_lib.Searcher(
    # list resources
    service="lambda",
    method="list_functions",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Functions"),
    # extract document
    doc_class=LambdaFunction,
    # search
    resource_type="lambda-function",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="description"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="func_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class LambdaLayer(res_lib.BaseDocument):
    description: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    layer_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            description=resource.get("LatestMatchingVersion", {}).get(
                "Description", "No Description"
            ),
            id=resource["LayerName"],
            name=resource["LayerName"],
            layer_arn=resource["LayerArn"],
        )

    @property
    def title(self) -> str:
        return self.name

    @property
    def subtitle(self) -> str:
        return self.description

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.layer_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.awslambda.get_layer(name_or_arn=self.arn + ":1")


lambda_layer_searcher = res_lib.Searcher(
    # list resources
    service="lambda",
    method="list_layers",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 1000, "PageSize": 50}},
    result_path=res_lib.ResultPath("Layers"),
    # extract document
    doc_class=LambdaLayer,
    # search
    resource_type="lambda-layer",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="description"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="layer_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

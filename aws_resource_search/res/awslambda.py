# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import zelfred.ui as zf

from .. import res_lib


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
        return self.name

    @property
    def subtitle(self) -> str:
        return self.description

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.func_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.awslambda.get_function(name_or_arn=self.arn)


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

    def details(self) -> T.List[zf.T_ITEM]:
        return [
            zf.Item(
                uid="1",
                title=f"Hello {self.arn}",
                subtitle=f"World {self.arn}",
            ),
        ]


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

# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value, ShortcutEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


lambda_function_state_icon = {
    "Pending": "🟡",
    "Active": "🟢",
    "Inactive": "⚫",
    "Failed": "🔴",
}


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
    def func_name(self) -> str:
        return self.name

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
            func_config = res["Configuration"]
            description = func_config.get("Description", "NA")
            role_arn = func_config["Role"]
            runtime = func_config["Runtime"]
            timeout = func_config["Timeout"]
            memory_size = func_config["MemorySize"]
            handler = func_config["Handler"]
            state = func_config.get("State", "NA")
            last_modified = func_config["LastModified"]
            architectures = func_config.get("Architectures", [])

            state_icon = lambda_function_state_icon[state]
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
                    Item("state", f"{state_icon} {state}"),
                    Item("last_modified", last_modified),
                    Item("architectures", architectures),
                ]
            )

            env_vars = func_config.get("Environment", {}).get("Variables", {})
            detail_items.extend(res_lib.DetailItem.from_env_vars(env_vars))

            tags: dict = res.get("Tags", {})
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        with self.enrich_details(detail_items):
            res = ars.bsm.lambda_client.list_event_source_mappings(
                FunctionName=self.arn,
            )
            mappings = res.get("EventSourceMappings", [])
            if len(mappings):
                for mapping in mappings:
                    event_source_uuid = mapping["UUID"]
                    event_source_arn = mapping["EventSourceArn"]
                    state = mapping["State"]
                    detail_items.append(
                        res_lib.DetailItem(
                            title="mapping: {}, {}".format(
                                format_key_value("event_source_arn", event_source_arn),
                                format_key_value("state", state),
                            ),
                            subtitle=f"🌐 {ShortcutEnum.ENTER} to open event source url, 📋 {ShortcutEnum.CTRL_A} to copy event sourec arn.",
                            uid=event_source_uuid,
                            variables={
                                "copy": event_source_arn,
                                "url": arns.Arn.from_arn(
                                    event_source_arn
                                ).to_console_url(),
                            },
                        )
                    )
            else:
                detail_items.append(
                    res_lib.DetailItem.new(
                        title=f"🔴 No mapping found",
                        subtitle=f"{ShortcutEnum.ENTER} to confirm in AWS console",
                        uid=f"no mapping found",
                        url=self.get_console_url(ars.aws_console),
                    )
                )

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
class LambdaAlias(res_lib.BaseDocument):
    description: str = dataclasses.field()
    func_name: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    alias_arn: str = dataclasses.field()

    @property
    def alias(self) -> str:
        return self.name

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        alias_arn = resource["AliasArn"]
        lbd_func = arns.res.LambdaFunction.from_arn(alias_arn)
        return cls(
            raw_data=resource,
            description=resource.get("Description", "No Description"),
            func_name=lbd_func.function_name,
            id=lbd_func.alias,
            name=lbd_func.alias,
            alias_arn=alias_arn,
        )

    @property
    def title(self) -> str:
        return format_key_value("alias", self.name)

    @property
    def subtitle(self) -> str:
        if not self.description:
            description = "No description"
        else:
            description = self.description
        return "{}, {}".format(
            description,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return f"{self.func_name}@{self.name}"

    @property
    def arn(self) -> str:
        return self.alias_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.awslambda.get_function_alias(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)

        with self.enrich_details(detail_items):
            res = ars.bsm.lambda_client.get_function_configuration(
                FunctionName=self.func_name,
                Qualifier=self.name,
            )
            description = res.get("Description", "NA")
            role_arn = res["Role"]
            runtime = res["Runtime"]
            timeout = res["Timeout"]
            memory_size = res["MemorySize"]
            handler = res["Handler"]
            state = res.get("State", "NA")
            last_modified = res["LastModified"]
            architectures = res.get("Architectures", [])

            state_icon = lambda_function_state_icon[state]
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
                    Item("state", f"{state_icon} {state}"),
                    Item("last_modified", last_modified),
                    Item("architectures", architectures),
                ]
            )

            env_vars = res.get("Environment", {}).get("Variables", {})
            detail_items.extend(res_lib.DetailItem.from_env_vars(env_vars))

        with self.enrich_details(detail_items):
            res = ars.bsm.lambda_client.list_event_source_mappings(
                FunctionName=self.arn,
            )
            mappings = res.get("EventSourceMappings", [])
            if len(mappings):
                for mapping in mappings:
                    event_source_uuid = mapping["UUID"]
                    event_source_arn = mapping["EventSourceArn"]
                    state = mapping["State"]
                    detail_items.append(
                        res_lib.DetailItem(
                            title="mapping: {}, {}".format(
                                format_key_value("event_source_arn", event_source_arn),
                                format_key_value("state", state),
                            ),
                            subtitle=f"🌐 {ShortcutEnum.ENTER} to open event source url, 📋 {ShortcutEnum.CTRL_A} to copy event sourec arn.",
                            uid=event_source_uuid,
                            variables={
                                "copy": event_source_arn,
                                "url": arns.Arn.from_arn(
                                    event_source_arn
                                ).to_console_url(),
                            },
                        )
                    )
            else:
                detail_items.append(
                    res_lib.DetailItem(
                        title=f"🔴 No mapping found",
                        uid=f"no mapping found",
                    )
                )

        return detail_items


lambda_function_alias_searcher = res_lib.Searcher(
    # list resources
    service="lambda",
    method="list_aliases",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Aliases"),
    # extract document
    doc_class=LambdaAlias,
    # search
    resource_type="lambda-alias",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="description"),
        res_lib.sayt.StoredField(name="func_name"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="alias_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=lambda boto_kwargs: [boto_kwargs["FunctionName"]],
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

# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value, ShortcutEnum
from ..searchers_enum import SearcherEnum

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
    @property
    def description(self) -> str:
        return res_lib.get_description(self.raw_data, "Description")

    @property
    def runtime(self) -> str:
        return self.raw_data.get("Runtime", "NA")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["FunctionName"],
            name=resource["FunctionName"],
        )

    @property
    def func_name(self) -> str:
        return self.name

    @property
    def title(self) -> str:
        return format_key_value("function_name", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}".format(
            format_key_value("runtime", self.runtime),
            format_key_value("description", self.description),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data["FunctionArn"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.awslambda.get_function(name_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.lambda_client.get_function(FunctionName=self.name)
            func_config = res["Configuration"]
            description = res_lib.get_description(func_config, "Description")
            role_arn = func_config["Role"]
            runtime = func_config.get("Runtime", "NA")
            timeout = func_config["Timeout"]
            memory_size = func_config["MemorySize"]
            handler = func_config["Handler"]
            state = func_config.get("State", "NA")
            last_modified = func_config["LastModified"]
            architectures = func_config.get("Architectures", [])

            state_icon = lambda_function_state_icon[state]
            detail_items.extend([
                from_detail("description", description, url=url),
                from_detail("🧢 role_arn", role_arn, url=ars.aws_console.iam.get_role(role_arn)),
                from_detail("runtime", runtime, url=url),
                from_detail("timeout", timeout, url=url),
                from_detail("memory_size", memory_size, url=url),
                from_detail("handler", handler, url=url),
                from_detail("state", f"{state_icon} {state}", url=url),
                from_detail("last_modified", last_modified, url=url),
                from_detail("architectures", architectures, url=url),
            ])

            detail_items.extend([
                from_detail(
                    "layer",
                    dct["Arn"],
                    url=ars.aws_console.awslambda.get_layer(name_or_arn=dct["Arn"]),
                )
                for dct in func_config.get("Layers", [])
            ])
            env_vars = func_config.get("Environment", {}).get("Variables", {})
            detail_items.extend(res_lib.DetailItem.from_env_vars(env_vars, url))

            tags: dict = res.get("Tags", {})
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

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
                        res_lib.DetailItem.new(
                            title="mapping: {}, {}".format(
                                format_key_value("event_source_arn", event_source_arn),
                                format_key_value("state", state),
                            ),
                            subtitle=f"🌐 {ShortcutEnum.ENTER} to open event source url, 📋 {ShortcutEnum.CTRL_A} to copy event sourec arn.",
                            uid=event_source_uuid,
                            copy=event_source_arn,
                            url=arns.Arn.from_arn(event_source_arn).to_console_url(),
                        )
                    )
            else:
                detail_items.append(
                    res_lib.DetailItem.new(
                        title=f"🔴 No mapping found",
                        subtitle=f"{ShortcutEnum.ENTER} to confirm in AWS console",
                        uid=f"no mapping found",
                        url=url,
                    )
                )

        return detail_items
    # fmt: on


class LambdaFunctionSearcher(res_lib.Searcher[LambdaFunction]):
    pass


lambda_function_searcher = LambdaFunctionSearcher(
    # list resources
    service="lambda",
    method="list_functions",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Functions"),
    # extract document
    doc_class=LambdaFunction,
    # search
    resource_type=SearcherEnum.lambda_function,
    fields=res_lib.define_fields(),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class LambdaFunctionAlias(res_lib.BaseDocument):
    @property
    def alias(self) -> str:
        return self.name

    @property
    def function_name(self) -> str:
        return self.arn.split(":")[-2]

    @property
    def description(self) -> str:
        return res_lib.get_description(self.raw_data, "Description")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        alias_arn = resource["AliasArn"]
        lbd_func = arns.res.LambdaFunction.from_arn(alias_arn)
        return cls(
            raw_data=resource,
            id=lbd_func.alias,
            name=lbd_func.alias,
        )

    @property
    def title(self) -> str:
        return format_key_value("alias", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}".format(
            self.description,
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return f"{self.function_name}@{self.name}"

    @property
    def arn(self) -> str:
        return self.raw_data["AliasArn"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.awslambda.get_function_alias(name_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        with self.enrich_details(detail_items):
            res = ars.bsm.lambda_client.get_function_configuration(
                FunctionName=self.function_name,
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
                    from_detail("description", description, url=url),
                    from_detail("🧢 role_arn", role_arn, url=ars.aws_console.iam.get_role(role_arn)),
                    from_detail("runtime", runtime, url=url),
                    from_detail("timeout", timeout, url=url),
                    from_detail("memory_size", memory_size, url=url),
                    from_detail("handler", handler, url=url),
                    from_detail("state", f"{state_icon} {state}", url=url),
                    from_detail("last_modified", last_modified, url=url),
                    from_detail("architectures", architectures, url=url),
                ]
            )

            env_vars = res.get("Environment", {}).get("Variables", {})
            detail_items.extend(res_lib.DetailItem.from_env_vars(env_vars, url))

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
                        res_lib.DetailItem.new(
                            title="mapping: {}, {}".format(
                                format_key_value("event_source_arn", event_source_arn),
                                format_key_value("state", state),
                            ),
                            subtitle=f"🌐 {ShortcutEnum.ENTER} to open event source url, 📋 {ShortcutEnum.CTRL_A} to copy event sourec arn.",
                            uid=event_source_uuid,
                            copy=event_source_arn,
                            url =arns.Arn.from_arn(event_source_arn).to_console_url(),
                        )
                    )
            else:
                detail_items.append(
                    res_lib.DetailItem.new(
                        title=f"🔴 No mapping found",
                        subtitle=f"{ShortcutEnum.ENTER} to confirm in AWS console",
                        uid=f"no mapping found",
                        url=url,
                    )
                )

        return detail_items
    # fmt: on


class LambdaFunctionAliasSearcher(res_lib.Searcher[LambdaFunctionAlias]):
    pass


lambda_function_alias_searcher = LambdaFunctionAliasSearcher(
    # list resources
    service="lambda",
    method="list_aliases",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
    result_path=res_lib.ResultPath("Aliases"),
    # extract document
    doc_class=LambdaFunctionAlias,
    # search
    resource_type=SearcherEnum.lambda_function_alias,
    fields=res_lib.define_fields(),
    cache_expire=24 * 60 * 60,
    more_cache_key=lambda boto_kwargs: [boto_kwargs["FunctionName"]],
)


@dataclasses.dataclass
class LambdaLayer(res_lib.BaseDocument):
    @property
    def description(self) -> str:
        return res_lib.get_description(
            self.raw_data,
            "LatestMatchingVersion.Description",
        )

    @property
    def compatible_runtimes(self) -> T.List[str]:
        return res_lib.get_none_or_default(
            self.raw_data,
            "LatestMatchingVersion.CompatibleRuntimes",
            [],
        )

    @property
    def compatible_architectures(self) -> T.List[str]:
        return res_lib.get_none_or_default(
            self.raw_data,
            "LatestMatchingVersion.CompatibleArchitectures",
            [],
        )

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["LayerName"],
            name=resource["LayerName"],
        )

    @property
    def title(self) -> str:
        return self.name

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}, {}".format(
            format_key_value("runtime", self.compatible_runtimes),
            format_key_value("arch", self.compatible_architectures),
            format_key_value("description", self.description),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data["LayerArn"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.awslambda.get_layer(name_or_arn=self.arn + ":1")


class LambdaLayerSearcher(res_lib.Searcher[LambdaLayer]):
    pass


lambda_layer_searcher = LambdaLayerSearcher(
    # list resources
    service="lambda",
    method="list_layers",
    is_paginator=True,
    default_boto_kwargs={"PaginationConfig": {"MaxItems": 1000, "PageSize": 50}},
    result_path=res_lib.ResultPath("Layers"),
    # extract document
    doc_class=LambdaLayer,
    # search
    resource_type=SearcherEnum.lambda_layer,
    fields=res_lib.define_fields(),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

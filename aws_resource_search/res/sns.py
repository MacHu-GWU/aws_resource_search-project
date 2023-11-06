# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class SnsTopic(res_lib.BaseDocument):
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        title = arns.res.SnsTopic.from_arn(resource["TopicArn"]).resource_id
        return cls(
            raw_data=resource,
            id=title,
            name=title,
        )

    @property
    def title(self) -> str:
        return format_key_value("name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data["TopicArn"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.sns.get_topic(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        # fmt: off
        with self.enrich_details(detail_items):
            res = ars.bsm.sns_client.get_topic_attributes(TopicArn=self.arn)
            access_policy = res.get("Attributes", {}).get("Policy")
            delivery_policy = res.get("Attributes", {}).get("DeliveryPolicy")
            subscriptions_confirmed = res.get("Attributes", {}).get("SubscriptionsConfirmed", "NA")
            subscriptions_deleted = res.get("Attributes", {}).get("SubscriptionsDeleted", "NA")
            subscriptions_pending = res.get("Attributes", {}).get("SubscriptionsPending", "NA")
            is_fifo_topic = res.get("Attributes", {}).get("FifoTopic", "NA")
            content_based_deduplication_enabled = res.get("Attributes", {}).get("ContentBasedDeduplication", "NA")
            detail_items.extend([
                from_detail("access_policy", access_policy, self.one_line(access_policy), url=url),
                from_detail("delivery_policy", delivery_policy, self.one_line(delivery_policy), url=url),
                from_detail("subscriptions_confirmed", subscriptions_confirmed, url=url),
                from_detail("subscriptions_deleted", subscriptions_deleted, url=url),
                from_detail("subscriptions_pending", subscriptions_pending, url=url),
                from_detail("is_fifo_topic", is_fifo_topic, url=url),
                from_detail("content_based_deduplication_enabled", content_based_deduplication_enabled, url=url),
            ])
        # fmt: on

        with self.enrich_details(detail_items):
            res = ars.bsm.sns_client.list_tags_for_resource(ResourceArn=self.arn)
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("Tags", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

        return detail_items


class SnsTopicSearcher(res_lib.Searcher[SnsTopic]):
    pass


sns_topic_searcher = SnsTopicSearcher(
    # list resources
    service="sns",
    method="list_topics",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {
            "MaxItems": 9999,
        },
    },
    result_path=res_lib.ResultPath("Topics"),
    # extract document
    doc_class=SnsTopic,
    # search
    resource_type=SearcherEnum.sns_topic,
    fields=res_lib.define_fields(),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

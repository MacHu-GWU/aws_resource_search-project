# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


@dataclasses.dataclass
class SnsTopic(rl.ResourceDocument):
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
        return rl.format_key_value("name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data["TopicArn"]

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.sns.get_topic(name_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.sns.topics

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.sns_client.get_topic_attributes(TopicArn=self.arn)
            access_policy = res.get("Attributes", {}).get("Policy")
            delivery_policy = res.get("Attributes", {}).get("DeliveryPolicy")
            subscriptions_confirmed = res.get("Attributes", {}).get("SubscriptionsConfirmed", "NA")
            subscriptions_deleted = res.get("Attributes", {}).get("SubscriptionsDeleted", "NA")
            subscriptions_pending = res.get("Attributes", {}).get("SubscriptionsPending", "NA")
            is_fifo_topic = res.get("Attributes", {}).get("FifoTopic", "NA")
            content_based_deduplication_enabled = res.get("Attributes", {}).get("ContentBasedDeduplication", "NA")
            detail_items.extend([
                from_detail("access_policy", access_policy, value_text=self.one_line(access_policy), url=url),
                from_detail("delivery_policy", delivery_policy, value_text=self.one_line(delivery_policy), url=url),
                from_detail("subscriptions_confirmed", subscriptions_confirmed, url=url),
                from_detail("subscriptions_deleted", subscriptions_deleted, url=url),
                from_detail("subscriptions_pending", subscriptions_pending, url=url),
                from_detail("is_fifo_topic", is_fifo_topic, url=url),
                from_detail("content_based_deduplication_enabled", content_based_deduplication_enabled, url=url),
            ])

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.sns_client.list_tags_for_resource(ResourceArn=self.arn)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


class SnsTopicSearcher(rl.BaseSearcher[SnsTopic]):
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
    result_path=rl.ResultPath("Topics"),
    # extract document
    doc_class=SnsTopic,
    # search
    resource_type=rl.SearcherEnum.sns_topic.value,
    fields=SnsTopic.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.sns_topic.value),
    more_cache_key=None,
)

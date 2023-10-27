# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib

if T.TYPE_CHECKING:
    from ..ars_v2 import ARS


@dataclasses.dataclass
class SnsTopic(res_lib.BaseDocument):
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    topic_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        title = arns.res.SnsTopic.from_arn(resource["TopicArn"]).resource_id
        return cls(
            raw_data=resource,
            id=title,
            name=title,
            topic_arn=resource["TopicArn"],
        )

    @property
    def title(self) -> str:
        return self.name

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.topic_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.sns.get_topic(name_or_arn=self.arn)

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        # fmt: off
        res = ars.bsm.sns_client.get_topic_attributes(TopicArn=self.arn)

        access_policy = res.get("Attributes", {}).get("Policy", "NA")
        delivery_policy = res.get("Attributes", {}).get("DeliveryPolicy", "NA")
        subscriptions_confirmed = res.get("Attributes", {}).get("SubscriptionsConfirmed", "NA")
        subscriptions_deleted = res.get("Attributes", {}).get("SubscriptionsDeleted", "NA")
        subscriptions_pending = res.get("Attributes", {}).get("SubscriptionsPending", "NA")
        is_fifo_topic = res.get("Attributes", {}).get("FifoTopic", "NA")
        content_based_deduplication_enabled = res.get("Attributes", {}).get("ContentBasedDeduplication", "NA")

        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        detail_items = [
            Item("arn", self.arn, url=aws.sns.get_topic(self.arn)),
            Item("access_policy", access_policy),
            Item("delivery_policy", delivery_policy),
            Item("subscriptions_confirmed", subscriptions_confirmed),
            Item("subscriptions_deleted", subscriptions_deleted),
            Item("subscriptions_pending", subscriptions_pending),
            Item("is_fifo_topic", is_fifo_topic),
            Item("content_based_deduplication_enabled", content_based_deduplication_enabled),
        ]
        # fmt: on

        res = ars.bsm.sns_client.list_tags_for_resource(ResourceArn=self.arn)
        tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("Tags", [])}
        tag_items = res_lib.DetailItem.from_tags(tags)
        return [
            *detail_items,
            *tag_items,
        ]


sns_topic_searcher = res_lib.Searcher(
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
    resource_type="sns-topic",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="topic_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

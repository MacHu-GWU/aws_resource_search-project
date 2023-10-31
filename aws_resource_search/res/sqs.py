# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import aws_arns.api as arns

from .. import res_lib
from ..terminal import format_key_value

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class SqsQueue(res_lib.BaseDocument):
    queue_url: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    queue_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        q = arns.res.SqsQueue.from_queue_url(url=resource)
        return cls(
            raw_data=resource,
            queue_url=resource,
            id=q.queue_name,
            name=q.queue_name,
            queue_arn=q.to_arn(),
        )

    @property
    def title(self) -> str:
        return format_key_value("name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.queue_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.sqs.get_queue(name_or_arn_or_url=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        detail_items.append(
            Item("queue_url", self.queue_url, url=self.get_console_url(ars.aws_console)),
        )

        with self.enrich_details(detail_items):
            res = ars.bsm.sqs_client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=["All"],
            )
            attrs = res.get("Attributes", {})
            is_fifo = attrs.get("FifoQueue", "NA")
            n_msg = attrs.get("ApproximateNumberOfMessages", "NA")
            n_msg_delayed = attrs.get("ApproximateNumberOfMessagesDelayed", "NA")
            n_msg_invisible = attrs.get("ApproximateNumberOfMessagesNotVisible", "NA")
            policy = attrs.get("Policy")
            redrive_policy = attrs.get("RedrivePolicy")
            redrive_allow_policy = attrs.get("RedriveAllowPolicy")
            detail_items.extend([
                Item("is_fifo", is_fifo),
                Item("n_msg", n_msg),
                Item("n_msg_delayed", n_msg_delayed),
                Item("n_msg_invisible", n_msg_invisible),
                Item("policy", self.one_line(policy)),
                Item("redrive_policy", self.one_line(redrive_policy)),
                Item("redrive_allow_policy", self.one_line(redrive_allow_policy)),
            ])

        with self.enrich_details(detail_items):
            res = ars.bsm.sqs_client.list_queue_tags(QueueUrl=self.queue_url)
            tags: dict = res.get("Tags", {})
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items
    # fmt: on


sqs_queue_searcher = res_lib.Searcher(
    # list resources
    service="sqs",
    method="list_queues",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {
            "MaxItems": 9999,
            "PageSize": 1000,
        },
    },
    result_path=res_lib.ResultPath("QueueUrls"),
    # extract document
    doc_class=SqsQueue,
    # search
    resource_type="sqs-queue",
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.StoredField(name="queue_url"),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="queue_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

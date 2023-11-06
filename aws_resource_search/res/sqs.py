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
class SqsQueue(res_lib.BaseDocument):
    queue_arn: str = dataclasses.field()

    @property
    def queue_url(self) -> str:
        return self.raw_data

    @property
    def queue_name(self) -> str:
        q = arns.res.SqsQueue.from_queue_url(url=self.queue_url)
        return q.queue_name

    @property
    def is_fifo(self) -> bool:
        return self.queue_name.endswith(".fifo")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        q = arns.res.SqsQueue.from_queue_url(url=resource)
        return cls(
            raw_data=resource,
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

    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        detail_items = self.get_initial_detail_items(ars)
        url = self.get_console_url(ars.aws_console)

        detail_items.extend([
            from_detail("queue_url", self.queue_url, url=url),
        ])

        # fmt: off
        with self.enrich_details(detail_items):
            res = ars.bsm.sqs_client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=["All"],
            )
            attrs = res.get("Attributes", {})
            is_fifo = self.is_fifo
            n_msg = attrs.get("ApproximateNumberOfMessages", "NA")
            n_msg_delayed = attrs.get("ApproximateNumberOfMessagesDelayed", "NA")
            n_msg_invisible = attrs.get("ApproximateNumberOfMessagesNotVisible", "NA")
            policy = attrs.get("Policy")
            redrive_policy = attrs.get("RedrivePolicy")
            redrive_allow_policy = attrs.get("RedriveAllowPolicy")
            detail_items.extend([
                from_detail("is_fifo", is_fifo, url=url),
                from_detail("n_msg", n_msg, url=url),
                from_detail("n_msg_delayed", n_msg_delayed, url=url),
                from_detail("n_msg_invisible", n_msg_invisible, url=url),
                from_detail("policy", policy, self.one_line(policy), url=url),
                from_detail("redrive_policy", redrive_policy, self.one_line(redrive_policy), url=url),
                from_detail("redrive_allow_policy", redrive_allow_policy, self.one_line(redrive_allow_policy), url=url),
            ])
        # fmt: on

        with self.enrich_details(detail_items):
            res = ars.bsm.sqs_client.list_queue_tags(QueueUrl=self.queue_url)
            tags: dict = res.get("Tags", {})
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))

        return detail_items


class SqsQueueSearcher(res_lib.Searcher[SqsQueue]):
    pass


sqs_queue_searcher = SqsQueueSearcher(
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
    resource_type=SearcherEnum.sqs_queue,
    fields=res_lib.define_fields(
        fields=[
            res_lib.sayt.StoredField(name="queue_arn"),
        ],
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)

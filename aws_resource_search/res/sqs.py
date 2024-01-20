# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import sayt.api as sayt
import aws_arns.api as arns
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


@dataclasses.dataclass
class SqsQueue(rl.ResourceDocument):
    # fmt: off
    queue_arn: str = dataclasses.field(metadata={"field": sayt.StoredField(name="queue_arn")})
    # fmt: on

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
        return rl.format_key_value("name", self.name)

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.queue_arn

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.sqs.get_queue(name_or_arn_or_url=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.sqs.queues

    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        detail_items.extend(
            [
                from_detail("queue_url", self.queue_url, url=url),
            ]
        )

        # fmt: off
        with rl.DetailItem.error_handling(detail_items):
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
                from_detail("policy", policy, value_text=self.one_line(policy), url=url),
                from_detail("redrive_policy", redrive_policy, value_text=self.one_line(redrive_policy), url=url),
                from_detail("redrive_allow_policy", redrive_allow_policy, value_text=self.one_line(redrive_allow_policy), url=url),
            ])
        # fmt: on

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.sqs_client.list_queue_tags(QueueUrl=self.queue_url)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items


class SqsQueueSearcher(rl.BaseSearcher[SqsQueue]):
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
    result_path=rl.ResultPath("QueueUrls"),
    # extract document
    doc_class=SqsQueue,
    # search
    resource_type=rl.SearcherEnum.sqs_queue.value,
    fields=SqsQueue.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.sqs_queue.value),
    more_cache_key=None,
)

# -*- coding: utf-8 -*-

"""
This module implements the logic to parse ``${service_id}.${resource_type}.url``
json node, and create aws console url that can view the given AWS resource detail.
"""

import typing as T
import dataclasses

from aws_console_url.api import AWSConsole

from .common import BaseModel
from .token import evaluate_token


@dataclasses.dataclass
class Url(BaseModel):
    """
    Defines how to create AWS console url string for a given AWS resource.

    .. note::

        This function is based on the `aws_console_url <https://github.com/MacHu-GWU/aws_console_url-project>`_
        Python library.

    Example:


        >>> from boto_session_manager import BotoSesManager
        >>> from aws_console_url.api import AWSConsole
        >>> bsm = BotoSesManager(profile_name="default")
        >>> aws_console = AWSConsole(
        ...     aws_account_id=bsm.aws_account_id,
        ...     aws_region=bsm.aws_region,
        ...     bsm=bsm,
        ... )
        >>> url = Url(service_id="s3", method="get_console_url", kwargs={"bucket": "$name"})
        >>> url.get(
        ...     document={
        ...         "id": "my-bucket",
        ...         "name": "my-bucket",
        ...         "raw_data": {"_res": {}, "_out": {}},
        ...     },
        ...     aws_console=aws_console,
        ... )
        'https://us-east-1.console.aws.amazon.com/s3/buckets/my-bucket?region=us-east-1&tab=objects'

    :param service_id: the attribute in ``aws_console_url.api.AWSConsole.${service_id}``.
        for example, ``s3``.
    :param method: the method in ``aws_console_url.api.AWSConsole.${service_id}.${method}``.
        for example, to get the console url for s3 bucket, the method is ``get_console_url``.
        you can find more detail at
        `aws_console_url public API document <https://github.com/MacHu-GWU/aws_console_url-project/blob/main/Public-API.rst#s3>`_
    :param kwargs: the key word arguments for ``aws_console_url.api.AWSConsole.${service_id}.${method}``.
        for example, to get the console url for s3 bucket, the argument is ``bucket="my-bucket"``,
        the value in kwargs can be a token that will be evaluated at runtime.
    """

    service_id: str = dataclasses.field()
    method: str = dataclasses.field()
    kwargs: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    def get(
        self,
        document: T.Dict[str, T.Any],
        aws_console: AWSConsole,
    ) -> str:
        """
        Get the aws console url using necessary data from the document.
        A document usually has a unique identifier ``id`` field, a human friendly
        ``name`` field that can be searched by ngram, and a ``raw_data`` field
        that contains the original boto3 api response and extracted output data.
        """
        kwargs = dict()
        for key, token in self.kwargs.items():
            kwargs[key] = evaluate_token(token, document)
        return getattr(getattr(aws_console, self.service_id), self.method)(**kwargs)


def parse_url_json_node(dct: T.Dict[str, T.Any]) -> Url:  # pragma: no cover
    return Url.from_dict(dct)

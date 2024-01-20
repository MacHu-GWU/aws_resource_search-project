# -*- coding: utf-8 -*-

"""
See :class:`ResourceTypeDocument`.
"""

import typing as T
import dataclasses

import sayt.api as sayt

from .base_document import BaseArsDocument


@dataclasses.dataclass
class ResourceTypeDocument(BaseArsDocument):
    """
    This is the AWS resource type document class. A resource type is a type of
    AWS resource, like s3-bucket, ec2-instance, etc.

    :param id: the maintainer defined unique identifier of the resource type,
        using hyphen-case.
    :param name: same as the ``id`` field, but using ``NgramWordsField`` for searching
    :param desc: the maintainer defined description for the specific resource type.
    :param ngram: ngram search string for the resource type.
    """

    id: str = dataclasses.field()
    name: str = dataclasses.field()
    desc: str = dataclasses.field()
    ngram: str = dataclasses.field()

    @classmethod
    def get_dataset_fields(cls) -> T.List[sayt.T_Field]:
        return [
            sayt.IdField(name="id", stored=True),
            sayt.NgramWordsField(name="name", stored=True, minsize=2, maxsize=20),
            sayt.StoredField(name="desc"),
            sayt.NgramWordsField(name="ngram", stored=True, minsize=2, maxsize=20),
        ]

# -*- coding: utf-8 -*-

"""
todo: add docstring
"""

import typing as T
import dataclasses


@dataclasses.dataclass
class BaseModel:
    """
    The base class for all AWS Resource data model.
    """

    @classmethod
    def from_dict(cls, data: T.Dict[str, T.Any]):
        """
        Create a new instance from a dict.
        """
        return cls(**data)

    def to_dict(self) -> T.Dict[str, T.Any]:
        """
        Convert the instance to a dict.
        """
        return dataclasses.asdict(self)


@dataclasses.dataclass
class BaseAwsResourceModel(BaseModel):
    aws_account_id: T.Optional[str] = dataclasses.field(default=None)
    aws_region: T.Optional[str] = dataclasses.field(default=None)
    arn: T.Optional[str] = dataclasses.field(default=None)
    console_url: T.Optional[str] = dataclasses.field(default=None)


@dataclasses.dataclass
class SearcherMetadata:
    """
    Example::

        {
            "id": "s3-bucket",
            "desc": "A bucket is a container for objects.",
            "ngram": "simple storage service"
        }
    """
    id: str = dataclasses.field()
    desc: str = dataclasses.field()
    ngram: str = dataclasses.field()
    module: str = dataclasses.field(default=None)
    klass: str = dataclasses.field(default=None)
    var: str = dataclasses.field(default=None)

    @property
    def id_snake(self) -> str:
        """
        Example::

            "s3_bucket"
        """
        return self.id.replace("-", "_")

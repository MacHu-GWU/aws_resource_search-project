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
        # new_data = {}
        # for field in dataclasses.fields(cls):
        #     if data.get(field.name) is not None:
        #         new_data[field.name] = data[field.name]
        # return cls(**new_data)

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

# -*- coding: utf-8 -*-

"""
Data model class.
"""

import typing as T
import dataclasses

from .vendor.better_dataclasses import DataClass


@dataclasses.dataclass
class BaseModel:
    """
    The base class for all AWS Resource data model.

    .. note::

        I intentionally don't use ``better_dataclasses.DataClass`` as the base class
        here. Because the AWS Resource data container is so heavily used in the
        search and performance does really matter. The ``better_dataclasses.DataClass``
        provides additional features like auto-serialization and deserialization
        when using nested dataclass. But it will slow down the performance.
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
class SearcherMetadata:
    """
    This class is a data container for the metadata of a :class:`Searcher` (todo fix this reference path).
    It describes the searcher's ID, description, and the path to the
    corresponding searcher module. It doesn't contain any data about
    the searcher's logic.

    This class is the data model for the ``aws_resource_search/searchers.json``

    This class is used heavily in the code generation process.

    .. seealso::

        :ref:`what-is-searcher`

    Example:

    .. code-block:: python

        SearcherMetadata(
            id="s3-bucket",
            desc="A bucket is a container for objects.",
            klass="S3BucketSearcher",
            module="s3",
            ngram="simple storage service",
            var="s3_bucket_searcher"
        )

    :param id: the maintainer defined unique identifier of the resource type,
        using hyphen-case.
    :param desc: the maintainer defined description for the specific resource type.
    :param ngram: ngram search string for the resource type.
    :param module: the path to the searcher module, for example,
        :mod:`/path/to/aws_resource_search/res/awslambda.py (aws_resource_search.res.awslambda) <aws_resource_search.res.awslambda>`
    :param klass: the class name in the searcher module, for example ``LambdaFunction``
    :param var: the variable name of the searcher class instance of the
        searcher module, for example ``lambda_function_searcher``.
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

    @property
    def id_slug(self) -> str:
        """
        Example::

            "s3-bucket"
        """
        return self.id.replace("_", "-")

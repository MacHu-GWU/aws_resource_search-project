# -*- coding: utf-8 -*-

"""
See :class:`SearcherMetadata`.
"""

import dataclasses

from .base_model import BaseModel


@dataclasses.dataclass
class SearcherMetadata(BaseModel):
    """
    This class is a data container for the metadata of a
    :class:`~aws_resource_search.base_searcher.BaseSearcher``.
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

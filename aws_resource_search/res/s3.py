# -*- coding: utf-8 -*-

"""
S3 related resources.

This module is an example of how to enable aws_resource_search to support new
resource types.
"""

import typing as T
import dataclasses

from .. import res_lib
from ..terminal import format_key_value

if T.TYPE_CHECKING:
    from ..ars import ARS


# Declare a new class for the resource type "S3 bucket".
# It is a searchable object stored in the index, representing the
# metadata of an AWS resource.
# The class name should be "${ServiceName}${ResourceName}" in camel case.
# it should inherit from res_lib.BaseDocument.
@dataclasses.dataclass
class S3Bucket(res_lib.BaseDocument):
    """
    S3 Bucket resource data model.
    """

    # declare the field names and types.
    # it has to have at least two fields: "id" and "name".
    # the id field is used to uniquely identify the resource, in this case,
    # it is the bucket name.
    # the name field is used to display the resource in the search result list
    # for most of AWS resource, it may have a "${resource_name}_arn" attribute.
    # most of AWS resource should store the ARN value as an attribute.
    # however, S3 bucket ARN can be calculated from the bucket name, so we
    # don't need to declare it here.
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    creation_date: str = dataclasses.field()

    # it has to have a class method named "from_resource", it converts the
    # the s3 bucket data in the response of boto3 s3_client.list_buckets method
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_buckets.html
    # to the S3Bucket object.
    # note that some attributes may not be available in the response,
    # so we should program defensively to provide a default value
    # for example, we could do creation_date = resource.get("CreationDate", "NA")
    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            id=resource["Name"],
            name=resource["Name"],
            creation_date=resource["CreationDate"].isoformat(),
        )

    # it has to have a property named "title", it is the first line of the
    # search result item in the dropdown menu. you can format the title using
    # terminal format and color
    # (Query): s3-bucket: my-bucket
    # [x] bucket_name = my-bucket # <--- THIS IS title
    #       create_at = 2020-01-01T00:00:00+00:00, 🌐 Enter, 📋 Ctrl A, 🔗 Ctrl U, 👀 Ctrl P.
    @property
    def title(self) -> str:
        """
        Example: :cyan:`bucket_name` = :yellow:`my-bucket`
        """
        return format_key_value("bucket_name", self.name)

    # it has to have a property named "subtitle", it is the second line of the
    # search result item in the dropdown menu. you can format the title using
    # terminal format and color
    # (Query): s3-bucket: my-bucket
    # [x] bucket_name = my-bucket
    #       create_at = 2020-01-01T00:00:00+00:00, 🌐 Enter, 📋 Ctrl A, 🔗 Ctrl U, 👀 Ctrl P. # <--- THIS IS subtitle
    @property
    def subtitle(self) -> str:
        """
        Example: :cyan:`create_at` = :yellow:`2021-07-06T15:04:40+00:00`,
        🌐 :magenta:`Enter`, 📋 :magenta:`Ctrl A`, 🔗 :magenta:`Ctrl U`, 👀 :magenta:`Ctrl P`.
        """
        return "{}, {}".format(
            format_key_value("create_at", self.creation_date),
            self.short_subtitle,
        )

    # it has to have a property named "autocomplete", it defines the text to be
    # fill in the query input box when the user tap 'Tab' for autocomplete
    # usually, it is the identifier of the resource, in this case, it is the s3 bucket name
    @property
    def autocomplete(self) -> str:
        """
        Automatically enter the bucket name.
        """
        return self.name

    # most of the AWS resource support ARN,
    # most of the time, the boto3 API will return the ARN value in the response,
    # so you can store that in the class attribute and just reference it in this
    # property. if the boto3 API doesn't return the ARN value, you have to define
    # a method to calculate the ARN value.
    @property
    def arn(self) -> str:
        """
        Example: ``arn:aws:s3:::my-bucket``
        """
        return f"arn:aws:s3:::{self.name}"

    # most of the AWS resource support console url,
    # you have to define a method to calculate the console url.
    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.s3.get_console_url(bucket=self.name)

    # the get_details method returns a list of items to be displayed in the
    # resource details view when user tap 'Ctrl P'.
    # you may call some boto3 API to get more details about the resource.
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        """
        Include s3 uri, s3 arn, bucket location and tags in details.
        """
        # the first code block is to initialize a detail_items list
        # using the class attribute
        Item = res_lib.DetailItem.from_detail
        aws = ars.aws_console
        url = self.get_console_url(aws)
        detail_items: T.List[res_lib.DetailItem] = [
            Item("s3 uri", f"s3://{self.name}", url=url),
            Item("s3 arn", self.arn, url=url),
        ]

        # the second code block is to call boto3 API to get more details
        # we should wrap the code block with ``self.enrich_details(detail_items)``
        # context manager because we may not have the permission
        # the context manager will catch the exception and add a debug message
        # to tell the user that we don't have the permission to call the API
        with self.enrich_details(detail_items):
            res = ars.bsm.s3_client.get_bucket_location(Bucket=self.name)
            location = res["LocationConstraint"]
            if not location:
                location = "us-east-1"
            detail_items.append(Item("location", location))

        # similar to the second code block
        with self.enrich_details(detail_items):
            res = ars.bsm.s3_client.get_bucket_policy(Bucket=self.name)
            detail_items.append(
                Item("bucket_policy", self.one_line(res.get("Policy", "{}")))
            )

        # the last code block is usually to get the tags of the resource
        with self.enrich_details(detail_items):
            res = ars.bsm.s3_client.get_bucket_tagging(Bucket=self.name)
            tags: dict = {dct["Key"]: dct["Value"] for dct in res.get("TagSet", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))

        return detail_items


# create a res_lib.Searcher object. It defines the search behavior including
# how to get the data, how to index the data, and how to search the data.
s3_bucket_searcher = res_lib.Searcher(
    # --- list resources
    # the s3 client argument in https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
    service="s3",
    # the method name in https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_buckets.html
    method="list_buckets",
    # is the above method a paginator?
    is_paginator=False,
    # is there any other arguments to pass to the above method?
    # if it is a paginator, usually you need to define the pagination config
    # {"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}}
    default_boto_kwargs=None,
    # how to access the list of resource data in the API response
    # you can find it in the "Response Syntax" section of
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_buckets.html
    result_path=res_lib.ResultPath("Buckets"),
    # --- extract document
    # what is the corresponding document class for this AWS resource?
    doc_class=S3Bucket,
    # --- search
    # the resource type identifier in string, the naming convention is
    # ${service_name}-${resource_name}
    resource_type="s3-bucket",
    # define how to index this document and how to search this document
    # the field list here has to match the attribute list in the document class
    # all field should be stored, so that we can recover the document object
    # from the search result
    fields=[
        # all document class has a "raw_data" field inheirt from res_lib.BaseDocument
        res_lib.sayt.StoredField(name="raw_data"),
        # the "id" field is the unique identifier of the document,
        # it should have higher weight (in field_boost) if this field is matched
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        # the name field should be n-gram searchable
        # and we would like to sort the result by name in ascending order
        # so we set the sortable and ascending to True
        res_lib.sayt.NgramWordsField(
            name="name",
            minsize=2,
            maxsize=4,
            stored=True,
            sortable=True,
            ascending=True,
        ),
        # the creation_date is just for rendering
        res_lib.sayt.StoredField(name="creation_date"),
    ],
    # the list_buckets API result will be cached for 24 hours, so that we don't
    # need to rebuild the index every time when user search
    # user can use !~ query to force refresh the index
    # you can update this value to extend the cache expire time
    cache_expire=24 * 60 * 60,
    # this is only used for child resource, we will cover it in the sfn.py file
    more_cache_key=None,
)

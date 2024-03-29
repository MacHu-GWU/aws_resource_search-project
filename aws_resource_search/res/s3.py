# -*- coding: utf-8 -*-

"""
S3 related resources.

This module is an example of how to enable aws_resource_search to support new
resource types.
"""

import typing as T
import json
import dataclasses
from datetime import datetime

import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


# Declare a new class for the resource type "S3 bucket".
# It is a searchable object stored in the index, representing the
# metadata of an AWS resource.
# The class name should be "${ServiceName}${ResourceName}" in camel case.
# it should inherit from res_lib.BaseDocument.
@dataclasses.dataclass
class S3Bucket(rl.ResourceDocument):
    """
    S3 Bucket resource data model.
    """

    # declare the field names and types.
    # for most of AWS resource, it may have a "${resource_name}_arn" attribute.
    # most of AWS resource should store the ARN value as an attribute.
    # however, S3 bucket ARN can be calculated from the bucket name, so we
    # don't need to declare it here.
    @property
    def creation_date(self) -> T.Optional[datetime]:
        return self.raw_data.get("CreationDate")

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
        )

    # it may have some additional property methods to provide more
    # human intuitive access to AWS resource attribute.
    @property
    def bucket_name(self) -> str:
        return self.name

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
        return rl.format_key_value("bucket_name", self.name)

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
            rl.format_key_value("create_at", self.creation_date),
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
    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.s3.get_console_url(bucket=self.name)

    # most of the AWS resource support list all resources of this type in AWS console,
    # you have to define a method to calculate the console url.
    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.s3.buckets

    # the get_details method returns a list of items to be displayed in the
    # resource details view when user tap 'Ctrl P'.
    # you may call some boto3 API to get more details about the resource.
    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        """
        Include s3 uri, s3 arn, bucket location and tags in details.
        """
        # the first code block is to initialize a detail_items list
        # using the class attribute
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        # get initial detail items
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars, arn_key="s3 arn")
        detail_items.append(from_detail("s3 uri", f"s3://{self.name}", url=url))

        # the second code block is to call boto3 API to get more details
        # we should wrap the code block with ``self.enrich_details(detail_items)``
        # context manager because we may not have the permission
        # the context manager will catch the exception and add a debug message
        # to tell the user that we don't have the permission to call the API
        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.s3_client.get_bucket_location(Bucket=self.name)
            location = res["LocationConstraint"]
            if not location:
                location = "us-east-1"
            detail_items.append(from_detail("location", location, url=url))

        # below, we call more API to get more information
        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.s3_client.get_bucket_versioning(Bucket=self.name)
            versioning = res.get("Status", "Not enabled yet")
            mfa_delete = res.get("MFADelete", "Not enabled yet")
            detail_items.extend([
                from_detail("versioning", versioning, url=url),
                from_detail("mfa_delete", mfa_delete, url=url),
            ])

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.s3_client.get_bucket_encryption(Bucket=self.name)
            rules = res.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
            if rules:
                rule = rules[0]
                sse_algorithm = rule.get("ApplyServerSideEncryptionByDefault", {}).get("SSEAlgorithm", "Unknown")
                kms_master_key_id = rule.get("ApplyServerSideEncryptionByDefault", {}).get("KMSMasterKeyID", "Unknown")
                bucket_key_enabled = rule.get("BucketKeyEnabled", "Unknown")
                detail_items.extend([
                    from_detail("sse_algorithm", sse_algorithm, url=url),
                    from_detail("kms_master_key_id", kms_master_key_id, url=url),
                    from_detail("bucket_key_enabled", bucket_key_enabled, url=url),
                ])

        # similar to the second code block
        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.s3_client.get_bucket_policy(Bucket=self.name)
            policy = res.get("Policy", "{}")
            detail_items.append(from_detail("bucket_policy", policy, self.one_line(policy), url=url))

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.s3_client.get_bucket_cors(Bucket=self.name)
            dct = {"CORSRules": res.get("CORSRules", [])}
            cors = json.dumps(dct)
            detail_items.append(from_detail("CORS", cors, self.one_line(cors), url=url))

        # the last code block is usually to get the tags of the resource
        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.s3_client.get_bucket_tagging(Bucket=self.name)
            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))

        return detail_items
    # fmt: on


# create a res_lib.Searcher object. It defines the search behavior including
# how to get the data, how to index the data, and how to search the data.
class S3BucketSearcher(rl.BaseSearcher[S3Bucket]):
    pass


s3_bucket_searcher = S3BucketSearcher(
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
    result_path=rl.ResultPath("Buckets"),
    # --- extract document
    # what is the corresponding document class for this AWS resource?
    doc_class=S3Bucket,
    # --- search
    # the resource type identifier in string, the naming convention is
    # ${service_name}-${resource_name}
    resource_type=rl.SearcherEnum.s3_bucket.value,
    # ``fields`` define how to index this document and how to search this document
    # the field list here has to match the attribute list in the document class
    # all field should be stored, so that we can recover the document object
    # from the search result
    fields=S3Bucket.get_dataset_fields(),
    # the list_buckets API result will be cached for 24 hours, so that we don't
    # need to rebuild the index every time when user search
    # user can use !~ query to force refresh the index
    # you can update this value to extend the cache expire time
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.s3_bucket.value),
    # this is only used for child resource, we will cover it in the sfn.py file
    more_cache_key=None,
)

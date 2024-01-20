# -*- coding: utf-8 -*-

import dataclasses

import pytest

import json
from datetime import datetime, timezone

import botocore.exceptions

import sayt.api as sayt
from aws_resource_search.documents.resource_type_document import (
    ResourceTypeDocument,
)


class TestResourceTypeDocument:
    def test_get_dataset_fields(self):
        ResourceTypeDocument.get_dataset_fields()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.documents.resource_type_document",
        preview=False,
    )

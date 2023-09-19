# -*- coding: utf-8 -*-

import pytest


def test():
    import aws_resource_search.api as aws_resource_search

    _ = aws_resource_search.CloudFormationSearcher
    _ = aws_resource_search.DynamoDBSearcher
    _ = aws_resource_search.IamSearcher
    _ = aws_resource_search.S3Searcher


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])

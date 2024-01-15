# -*- coding: utf-8 -*-


def test():
    import aws_resource_search.api as aws_resource_search

    _ = aws_resource_search.ARS


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.api", preview=False)

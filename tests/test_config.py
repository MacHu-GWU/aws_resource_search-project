# -*- coding: utf-8 -*-


from aws_resource_search.conf.define import Config, SearcherEnum
from rich import print as rprint


def test():
    config = Config.load()
    for searcher_enum in SearcherEnum:
        config.get_cache_expire(searcher_enum.value)


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.conf.define", preview=False)

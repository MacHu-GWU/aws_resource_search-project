# -*- coding: utf-8 -*-

from aws_resource_search.service_searcher import srv_and_res_ds
from rich import print

if __name__ == "__main__":
    res = srv_and_res_ds.search(download_kwargs={}, query="buc")
    print(res)
# -*- coding: utf-8 -*-

import shutil

from ..paths import dir_aws_resource_search, dir_index, dir_cache


def main():
    print(f"clear index in {dir_index}")
    if dir_index.exists():
        shutil.rmtree(dir_index, ignore_errors=True)
    print(f"clear cache in {dir_cache}")
    if dir_cache.exists():
        shutil.rmtree(dir_cache, ignore_errors=True)
    print(f"done, you can verify at file://{dir_aws_resource_search}")

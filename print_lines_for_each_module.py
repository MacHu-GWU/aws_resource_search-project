# -*- coding: utf-8 -*-

from pathlib_mate import Path

dir_python_lib = Path.dir_here(__file__).joinpath("aws_resource_search")
for p in dir_python_lib.select_by_ext(".py"):
    relpath = p.relative_to(dir_python_lib)
    n_lines = p.read_text().count("\n")
    print(f"{relpath}: {n_lines}")

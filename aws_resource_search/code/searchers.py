# -*- coding: utf-8 -*-

import typing as T
import importlib

import jinja2
from pathlib import Path

from ..paths import dir_python_lib
from ..res_lib import Searcher

dir_here = Path(__file__).absolute().parent
path_tpl = dir_here.joinpath("searchers.py.jinja")
path_py = dir_python_lib.joinpath("searchers.py")


def generate_searchers_py_module():
    tuples: T.List[T.Tuple[str, str, str, str]] = list()
    for p in dir_python_lib.joinpath("res").iterdir():
        if p.name.startswith("__"):
            continue
        module_name = p.stem
        module = importlib.import_module(f"aws_resource_search.res.{module_name}")
        for var_name, value in module.__dict__.items():
            if isinstance(value, Searcher):
                tuples.append(
                    (
                        value.resource_type.replace("-", "_"),
                        value.resource_type,
                        module_name,
                        var_name,
                    )
                )
    tuples = list(sorted(tuples, key=lambda x: x[0]))
    tpl = jinja2.Template(path_tpl.read_text())
    path_py.write_text(tpl.render(tuples=tuples))

# -*- coding: utf-8 -*-

import typing as T
import importlib

import jinja2
from pathlib import Path

from ..paths import dir_python_lib, dir_project_root
from ..res_lib import Searcher

dir_here = Path(__file__).absolute().parent


def get_searcher_py_modules() -> T.List[T.Tuple[str, str, str, str]]:
    py_modules: T.List[T.Tuple[str, str, str, str]] = list()
    for p in dir_python_lib.joinpath("res").iterdir():
        if p.name.startswith("__"):
            continue
        module_name = p.stem
        module = importlib.import_module(f"aws_resource_search.res.{module_name}")
        for var_name, value in module.__dict__.items():
            if isinstance(value, Searcher):
                resource_type_snake = value.resource_type.replace("-", "_")
                resource_type = value.resource_type
                py_modules.append(
                    (
                        resource_type_snake,
                        resource_type,
                        module_name,
                        var_name,
                    )
                )
    py_modules = list(sorted(py_modules, key=lambda x: x[0]))
    return py_modules


py_modules = get_searcher_py_modules()


def generate_searchers_py_module(py_modules):
    path_tpl = dir_here.joinpath("searchers.py.jinja")
    path_py = dir_python_lib.joinpath("searchers.py")
    tpl = jinja2.Template(path_tpl.read_text())
    path_py.write_text(tpl.render(tuples=py_modules))


def generate_implemented_resource_types(py_modules):
    dir_folder = dir_project_root.joinpath("docs", "source", "03-User-Guide-Implemented-AWS-Resource-Types")
    path_tpl = dir_here.joinpath("searchers_index.rst.jinja")
    path_index = dir_folder.joinpath("index.rst")
    tpl = jinja2.Template(path_tpl.read_text())
    path_index.write_text(tpl.render(tuples=py_modules))

# -*- coding: utf-8 -*-

import typing as T
import json
import importlib

import jinja2
from pathlib import Path

from ..paths import dir_project_root, dir_python_lib, path_searchers_json
from ..res_lib import Searcher
from ..model import SearcherMetadata

dir_here = Path(__file__).absolute().parent


def load_raw_searcher_metadata_list() -> T.List[SearcherMetadata]:
    """
    Parse the searcher.json file.
    """
    data = json.loads(path_searchers_json.read_text())
    sr_meta_list = list()
    for id, dct in data.items():
        desc, ngram = dct["desc"], dct["ngram"]
        sr_meta = SearcherMetadata(id=id, desc=desc, ngram=ngram)
        sr_meta_list.append(sr_meta)
    return sr_meta_list


def sort_searcher_metadata_list(sr_meta_list: T.List[SearcherMetadata]):
    """
    Sort searcher_metadata by id
    """
    sr_meta_list = list(sorted(sr_meta_list, key=lambda x: x.id))
    return sr_meta_list


def dump_raw_searcher_metadata_list(sr_meta_list: T.List[SearcherMetadata]):
    """
    Dump searcher_metadata to searcher.json file.
    """
    path_searchers_json.write_text(json.dumps(sr_meta_list, indent=4, sort_keys=True))


def generate_searchers_enum_py_module(sr_meta_list: T.List[SearcherMetadata]):
    path_tpl = dir_here.joinpath("searchers_enum.py.jinja")
    path_py = dir_python_lib.joinpath("searchers_enum.py")
    tpl = jinja2.Template(path_tpl.read_text())
    path_py.write_text(tpl.render(sr_meta_list=sr_meta_list))

# def enrich_searcher_metadata(sr_meta_list: T.List[SearcherMetadata]):
#     # py_modules: T.List[T.Tuple[str, str, str, str]] = list()
#     sr_meta_dct_view: T.Dict[str, SearcherMetadata] = {
#         sr_meta.id: sr_meta for sr_meta in sr_meta_list
#     }
#     for p in dir_python_lib.joinpath("res").iterdir():
#         if p.name.startswith("__"):
#             continue
#         module_name = p.stem
#         module = importlib.import_module(f"aws_resource_search.res.{module_name}")
#         for var_name, value in module.__dict__.items():
#             if isinstance(value, Searcher):
#                 sr_meta_dct_view[value.resource_type].module = module_name
#                 sr_meta_dct_view[value.resource_type].var = var_name


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
    dir_folder = dir_project_root.joinpath(
        "docs", "source", "03-User-Guide-Implemented-AWS-Resource-Types"
    )
    path_tpl = dir_here.joinpath("searchers_index.rst.jinja")
    path_index = dir_folder.joinpath("index.rst")
    tpl = jinja2.Template(path_tpl.read_text())
    path_index.write_text(tpl.render(tuples=py_modules))

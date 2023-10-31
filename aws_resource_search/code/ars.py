# -*- coding: utf-8 -*-

import jinja2
from pathlib import Path

from ..paths import dir_python_lib
from ..searchers import searchers_metadata

dir_here = Path(__file__).absolute().parent
path_tpl = dir_here.joinpath("ars.py.jinja")
path_py = dir_python_lib.joinpath("ars.py")


def generate_ars_py_module():
    """
    Generate ``aws_resource_search/ars_v2.py`` module.
    """
    tuples = [
        (resource_type.replace("-", "_"), resource_type) for resource_type in searchers_metadata
    ]
    tuples = list(sorted(tuples, key=lambda x: x[0]))
    tpl = jinja2.Template(path_tpl.read_text())
    path_py.write_text(tpl.render(tuples=tuples))

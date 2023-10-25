# -*- coding: utf-8 -*-

import jinja2
from pathlib import Path

from ..paths import dir_python_lib
from ..searchers import lookup

dir_here = Path(__file__).absolute().parent
path_tpl = dir_here.joinpath("ars_v2.py.jinja")
path_py = dir_python_lib.joinpath("searchers.py")



def generate_ars_py_module():
    """
    Generate ``aws_resource_search/ars.py`` module.
    """
    path_tpl = dir_here.joinpath("ars.py.jinja")
    path_py = dir_aws_resource_search.joinpath("ars.py")
    ars = ARSBase(bsm=None)
    tpl = jinja2.Template(path_tpl.read_text())
    path_py.write_text(
        tpl.render(
            service_id_resource_type_pairs=ars._service_id_and_resource_type_pairs()
        )
    )

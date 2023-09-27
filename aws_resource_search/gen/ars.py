# -*- coding: utf-8 -*-

import jinja2
from pathlib import Path
from ..ars_base import ARSBase

dir_here = Path(__file__).absolute().parent
dir_aws_resource_search = dir_here.parent
path_tpl = dir_here.joinpath("ars.py.jinja")
path_py = dir_aws_resource_search.joinpath("ars.py")


def gen_code():
    ars = ARSBase(bsm=None)
    tpl = jinja2.Template(path_tpl.read_text())
    path_py.write_text(tpl.render(service_id_resource_type_pairs=ars._service_id_and_resource_type_pairs()))

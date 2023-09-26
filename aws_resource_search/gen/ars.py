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
    pairs = list()
    for service_id, dct in ars.data.items():
        if not service_id.startswith("_"):
            for resource_type in dct:
                if not resource_type.startswith("_"):
                    pairs.append((service_id, resource_type))
    tpl = jinja2.Template(path_tpl.read_text())
    path_py.write_text(tpl.render(service_id_resource_type_pairs=pairs))

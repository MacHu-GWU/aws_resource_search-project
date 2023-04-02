# -*- coding: utf-8 -*-

from pathlib_mate import Path

_dir_here = Path.dir_here(__file__)

dir_project_root = _dir_here.parent

# ------------------------------------------------------------------------------
# ${HOME}/.aws_console_url_search/ dir related
# ------------------------------------------------------------------------------
dir_home = Path.home()
dir_aws_console_url_search = dir_home.joinpath(".aws_resource_search")
dir_cache = dir_aws_console_url_search.joinpath("cache")

# ------------------------------------------------------------------------------
# test related
# ------------------------------------------------------------------------------
dir_tests = dir_project_root.joinpath("tests")

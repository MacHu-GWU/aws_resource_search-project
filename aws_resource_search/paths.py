# -*- coding: utf-8 -*-

from pathlib_mate import Path

_dir_here = Path.dir_here(__file__)

dir_project_root = _dir_here.parent

# ------------------------------------------------------------------------------
# Virtual Environment Related
# ------------------------------------------------------------------------------
dir_venv = dir_project_root / ".venv"
dir_venv_bin = dir_venv / "bin"

# virtualenv executable paths
bin_pytest = dir_venv_bin / "pytest"

# test related
dir_htmlcov = dir_project_root / "htmlcov"
path_cov_index_html = dir_htmlcov / "index.html"
dir_unit_test = dir_project_root / "tests"

# ------------------------------------------------------------------------------
# ${HOME}/.aws_console_url_search/ dir related
# ------------------------------------------------------------------------------
dir_home = Path.home()
dir_aws_console_url_search = dir_home.joinpath(".aws_resource_search")
dir_cache = dir_aws_console_url_search.joinpath("cache")

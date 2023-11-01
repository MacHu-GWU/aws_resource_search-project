# -*- coding: utf-8 -*-

from pathlib_mate import Path

dir_python_lib = Path.dir_here(__file__)

dir_project_root = dir_python_lib.parent

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
dir_aws_resource_search = dir_home.joinpath(".aws_resource_search")
dir_aws_resource_search.mkdir(exist_ok=True)

dir_index = dir_aws_resource_search.joinpath(".index")
dir_cache = dir_aws_resource_search.joinpath(".cache")
path_config_json = dir_aws_resource_search.joinpath("config.json")

# ------------------------------------------------------------------------------
# Project
# ------------------------------------------------------------------------------
path_data_json = dir_python_lib.joinpath("data.json")

# -*- coding: utf-8 -*-

from pathlib import Path

dir_python_lib = Path(__file__).absolute().parent

dir_project_root = dir_python_lib.parent

# ------------------------------------------------------------------------------
# Source code related
# ------------------------------------------------------------------------------
path_searchers_json = dir_python_lib.joinpath("searchers.json")

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
# ${HOME}/.aws_resource_search/ dir related
# ------------------------------------------------------------------------------
dir_home = Path.home()
dir_aws_resource_search = dir_home.joinpath(".aws_resource_search")
dir_aws_resource_search.mkdir(exist_ok=True)

dir_index = dir_aws_resource_search.joinpath(".index")
dir_cache = dir_aws_resource_search.joinpath(".cache")
path_config_json = dir_aws_resource_search.joinpath("config.json")
path_exception_item_txt = dir_aws_resource_search.joinpath("exception_item.txt")

# ------------------------------------------------------------------------------
# ${HOME}/.aws/ dir
# ------------------------------------------------------------------------------
dir_aws = dir_home.joinpath(".aws")
path_aws_config = dir_aws.joinpath("config")
path_aws_credentials = dir_aws.joinpath("credentials")

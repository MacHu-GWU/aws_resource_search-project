# -*- coding: utf-8 -*-

import os
from aws_resource_search.tests.mock_aws_cli import test_home_aws_folder

if "CI" in os.environ:
    test_home_aws_folder.setup()

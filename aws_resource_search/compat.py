# -*- coding: utf-8 -*-

import sys

if sys.version_info.major == 2 or (
    sys.version_info.major == 3 and sys.version_info.minor < 6
):  # pragma: no cover
    raise NotImplementedError("we don't support < Python3.6!")

if sys.version_info.minor < 8:  # pragma: no cover
    from cached_property import cached_property
    from typing_extensions import TypedDict
else:  # pragma: no cover
    from functools import cached_property
    from typing import TypedDict

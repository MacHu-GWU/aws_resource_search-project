# -*- coding: utf-8 -*-

"""
This module manages the underlying boto3 session for the UI. It always uses
the default url. You could use the `awscli_mate <https://github.com/MacHu-GWU/awscli_mate-project>`_
tool to set any given profile as default.
"""

import botocore.exceptions
from boto_session_manager import BotoSesManager

from ..ars import ARS
from ..exc import MalformedBotoSessionError

bsm = BotoSesManager()
ars = ARS(bsm=bsm)

# validate the boto session manager
try:
    _ = bsm.aws_account_id
except Exception as e:  # pragma: no cover
    raise MalformedBotoSessionError(
        f"failed to use sts.get_caller_identity() to get AWS account id:, "
        f"please check your default AWS profile in ~/.aws/config and ~/.aws/credentials, "
        f"error: {e}"
    )

try:
    _ = bsm.aws_region
except Exception as e:  # pragma: no cover
    raise MalformedBotoSessionError(
        f"failed to get AWS region of your boto session, "
        f"please check your default AWS profile in ~/.aws/config and ~/.aws/credentials, "
        f"error: {e}"
    )

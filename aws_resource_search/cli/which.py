# -*- coding: utf-8 -*-

import botocore.exceptions

from ..ui.boto_ses import bsm


def main():
    print(f"AWS Account ID = {bsm.aws_account_id}")
    try:
        res = bsm.iam_client.list_account_aliases()
        aliases = res.get("AccountAliases", [])
        if aliases:
            print(f"AWS Account Alias = {aliases[0]}")
    except botocore.exceptions.ClientError as e:
        pass
    print(f"AWS Region = {bsm.aws_region}")

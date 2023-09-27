# -*- coding: utf-8 -*-

from aws_resource_search.ars import ARS
from boto_session_manager import BotoSesManager
from rich import print as rprint

bsm = BotoSesManager(profile_name="edf_sbx_eu_west_1_mfa", region_name="eu-west-1")


if __name__ == "__main__":
    ars = ARS(bsm=bsm)

    query = "gesa 956"
    # refresh_data = True
    refresh_data = False
    limit = 5
    # docs = ars.cloudformation_stack.query("gesa 956", limit=limit, refresh_data=refresh_data)
    # docs = ars.ec2_instance.query("gesa", limit=limit, refresh_data=refresh_data)
    docs = ars.s3_bucket.query("gesa 956", limit=5, refresh_data=refresh_data)
    print(f"number of docs: {len(docs)}")
    for doc in docs:
        print(doc["name"], doc["console_url"])

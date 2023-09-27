# -*- coding: utf-8 -*-

from aws_resource_search.ars import ARS
from boto_session_manager import BotoSesManager
from rich import print as rprint

bsm = BotoSesManager(profile_name="edf_sbx_eu_west_1_mfa", region_name="eu-west-1")


if __name__ == "__main__":
    ars = ARS(bsm=bsm)

    query = "*"
    # refresh_data = True
    refresh_data = False
    limit = 20

    # docs = ars.cloudformation_stack.query(query, limit=limit, refresh_data=refresh_data)
    # docs = ars.ec2_instance.query(query, limit=limit, refresh_data=refresh_data)
    # docs = ars.glue_database.query(query, limit=limit, refresh_data=refresh_data)
    # docs = ars.glue_job.query(query, limit=limit, refresh_data=refresh_data)
    # docs = ars.glue_crawler.query(query, limit=limit, refresh_data=refresh_data)
    # docs = ars.iam_role.query(query, limit=limit, refresh_data=refresh_data)
    docs = ars.s3_bucket.query(query, limit=5, refresh_data=refresh_data)
    print(f"number of docs: {len(docs)}")
    for doc in docs:
        print(doc["id"], doc["name"], doc["console_url"])

    # docs = ars.glue_database.query(query, limit=limit, refresh_data=refresh_data)
    # db_name = docs[0]["name"]
    # docs = ars.glue_table.query(
    #     query,
    #     limit=limit,
    #     boto_kwargs={"DatabaseName": db_name},
    #     refresh_data=refresh_data,
    # )
    # for doc in docs:
    #     print(doc["id"], doc["name"], doc["console_url"])

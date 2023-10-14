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

    # docs = ars.cloudformation_stack.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    # docs = ars.ec2_instance.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    # docs = ars.ec2_vpc.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    # docs = ars.ec2_securitygroup.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    # docs = ars.glue_database.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    # docs = ars.glue_job.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    # docs = ars.glue_crawler.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    # docs = ars.iam_role.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    # docs = ars.s3_bucket.search(query, limit=5, refresh_data=refresh_data, simple_response=True)
    # print(f"number of docs: {len(docs)}")
    # docs = ars.cloudformation_stack.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    # docs = ars.lambda_function.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    docs = ars.lambda_layer.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    for doc in docs:
        # print(doc)
        print(doc["id"], doc["name"], doc["console_url"], doc["raw_data"]["_out"]["subtitle"])

    # docs = ars.glue_database.search(query, limit=limit, refresh_data=refresh_data, simple_response=True)
    # db_name = docs[0]["name"]
    # docs = ars.glue_table.search(
    #     query,
    #     limit=limit,
    #     boto_kwargs={"DatabaseName": db_name},
    #     refresh_data=refresh_data,
    #     simple_response=True,
    # )
    # for doc in docs:
    #     print(doc["id"], doc["name"], doc["console_url"])

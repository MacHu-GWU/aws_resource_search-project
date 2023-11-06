# -*- coding: utf-8 -*-

"""
This script helps developer to debug specific AWS resource type searcher.
"""

from rich import print as rprint
from aws_resource_search.ui.boto_ses import bsm, ars


if __name__ == "__main__":
    # --------------------------------------------------------------------------
    query = "*"
    limit = 50
    boto_kwargs = {}
    refresh_data = True
    simple_response = True
    verbose = False
    # --------------------------------------------------------------------------
    # sr = ars.cloudformation_stack
    # sr = ars.codebuild_job_run
    # sr = ars.codebuild_project
    # sr = ars.codecommit_repository
    # sr = ars.codepipeline_pipeline
    # sr = ars.dynamodb_table
    # sr = ars.ec2_instance
    # sr = ars.ec2_security_group
    # sr = ars.ec2_subnet
    # sr = ars.ec2_vpc
    # sr = ars.glue_crawler
    # sr = ars.glue_database
    # sr = ars.glue_database_table
    # sr = ars.glue_job
    # sr = ars.glue_job_run
    # sr = ars.iam_group
    # sr = ars.iam_policy
    # sr = ars.iam_role
    # sr = ars.iam_user
    # sr = ars.kms_key_alias
    # sr = ars.lambda_function
    # sr = ars.lambda_function_alias
    # sr = ars.lambda_layer
    # sr = ars.rds_db_cluster
    # sr = ars.rds_db_instance
    sr = ars.s3_bucket
    # sr = ars.secretsmanager_secret
    # sr = ars.sfn_state_machine
    # sr = ars.sfn_state_machine_execution
    # sr = ars.sns_topic
    # sr = ars.sqs_queue
    # sr = ars.ssm_parameter
    # --------------------------------------------------------------------------
    res = sr.search(
        bsm=bsm,
        query=query,
        limit=limit,
        boto_kwargs=boto_kwargs,
        refresh_data=refresh_data,
        verbose=verbose,
    )

    # print(res[0].raw_data) # this is for type hint test

    if isinstance(res, dict):
        hits = res.pop("hits")
        docs = [hit["_source"] for hit in hits]
        rprint(res)
    else:
        docs = res

    # for doc in res:
    for doc in res[:3]:
        rprint(doc)
        print(doc.get_console_url(ars.aws_console))

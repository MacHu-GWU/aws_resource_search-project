# -*- coding: utf-8 -*-

searchers_metadata = {
    "codecommit-repository": {"mod": "codecommit", "var": "codecommit_repository_searcher"},
    "ec2-instance": {"mod": "ec2", "var": "ec2_instance_searcher"},
    "ec2-securitygroup": {"mod": "ec2", "var": "ec2_securitygroup_searcher"},
    "ec2-subnet": {"mod": "ec2", "var": "ec2_subnet_searcher"},
    "ec2-vpc": {"mod": "ec2", "var": "ec2_vpc_searcher"},
    "glue-database": {"mod": "glue", "var": "glue_database_searcher"},
    "glue-job": {"mod": "glue", "var": "glue_job_searcher"},
    "glue-jobrun": {"mod": "glue", "var": "glue_job_run_searcher"},
    "glue-table": {"mod": "glue", "var": "glue_table_searcher"},
    "iam-group": {"mod": "iam", "var": "iam_group_searcher"},
    "iam-policy": {"mod": "iam", "var": "iam_policy_searcher"},
    "iam-role": {"mod": "iam", "var": "iam_role_searcher"},
    "iam-user": {"mod": "iam", "var": "iam_user_searcher"},
    "lambda-function": {"mod": "awslambda", "var": "lambda_function_searcher"},
    "lambda-layer": {"mod": "awslambda", "var": "lambda_layer_searcher"},
    "s3-bucket": {"mod": "s3", "var": "s3_bucket_searcher"},
    "sfn-execution": {"mod": "sfn", "var": "sfn_execution_searcher"},
    "sfn-statemachine": {"mod": "sfn", "var": "sfn_state_machine_searcher"},
}

class SearcherEnum:
    codecommit_repository = "codecommit-repository"
    ec2_instance = "ec2-instance"
    ec2_securitygroup = "ec2-securitygroup"
    ec2_subnet = "ec2-subnet"
    ec2_vpc = "ec2-vpc"
    glue_database = "glue-database"
    glue_job = "glue-job"
    glue_jobrun = "glue-jobrun"
    glue_table = "glue-table"
    iam_group = "iam-group"
    iam_policy = "iam-policy"
    iam_role = "iam-role"
    iam_user = "iam-user"
    lambda_function = "lambda-function"
    lambda_layer = "lambda-layer"
    s3_bucket = "s3-bucket"
    sfn_execution = "sfn-execution"
    sfn_statemachine = "sfn-statemachine"
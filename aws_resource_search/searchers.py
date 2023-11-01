# -*- coding: utf-8 -*-

searchers_metadata = {
    "cloudformation-stack": {"mod": "cloudformation", "var": "cloudformation_stack_searcher"},
    "codecommit-repository": {"mod": "codecommit", "var": "codecommit_repository_searcher"},
    "dynamodb-table": {"mod": "dynamodb", "var": "dynamodb_table_searcher"},
    "ec2-instance": {"mod": "ec2", "var": "ec2_instance_searcher"},
    "ec2-securitygroup": {"mod": "ec2", "var": "ec2_securitygroup_searcher"},
    "ec2-subnet": {"mod": "ec2", "var": "ec2_subnet_searcher"},
    "ec2-vpc": {"mod": "ec2", "var": "ec2_vpc_searcher"},
    "glue-crawler": {"mod": "glue", "var": "glue_crawler_searcher"},
    "glue-database": {"mod": "glue", "var": "glue_database_searcher"},
    "glue-job": {"mod": "glue", "var": "glue_job_searcher"},
    "glue-jobrun": {"mod": "glue", "var": "glue_job_run_searcher"},
    "glue-table": {"mod": "glue", "var": "glue_table_searcher"},
    "iam-group": {"mod": "iam", "var": "iam_group_searcher"},
    "iam-policy": {"mod": "iam", "var": "iam_policy_searcher"},
    "iam-role": {"mod": "iam", "var": "iam_role_searcher"},
    "iam-user": {"mod": "iam", "var": "iam_user_searcher"},
    "kms-alias": {"mod": "kms", "var": "kms_key_alias_searcher"},
    "lambda-function": {"mod": "awslambda", "var": "lambda_function_searcher"},
    "lambda-layer": {"mod": "awslambda", "var": "lambda_layer_searcher"},
    "s3-bucket": {"mod": "s3", "var": "s3_bucket_searcher"},
    "secretsmanager-secret": {"mod": "secretmanager", "var": "secretsmanager_secret_searcher"},
    "sfn-execution": {"mod": "sfn", "var": "sfn_execution_searcher"},
    "sfn-statemachine": {"mod": "sfn", "var": "sfn_state_machine_searcher"},
    "sns-topic": {"mod": "sns", "var": "sns_topic_searcher"},
    "sqs-queue": {"mod": "sqs", "var": "sqs_queue_searcher"},
    "ssm-parameter": {"mod": "ssm", "var": "ssm_parameter_searcher"},
}

class SearcherEnum:
    cloudformation_stack = "cloudformation-stack"
    codecommit_repository = "codecommit-repository"
    dynamodb_table = "dynamodb-table"
    ec2_instance = "ec2-instance"
    ec2_securitygroup = "ec2-securitygroup"
    ec2_subnet = "ec2-subnet"
    ec2_vpc = "ec2-vpc"
    glue_crawler = "glue-crawler"
    glue_database = "glue-database"
    glue_job = "glue-job"
    glue_jobrun = "glue-jobrun"
    glue_table = "glue-table"
    iam_group = "iam-group"
    iam_policy = "iam-policy"
    iam_role = "iam-role"
    iam_user = "iam-user"
    kms_alias = "kms-alias"
    lambda_function = "lambda-function"
    lambda_layer = "lambda-layer"
    s3_bucket = "s3-bucket"
    secretsmanager_secret = "secretsmanager-secret"
    sfn_execution = "sfn-execution"
    sfn_statemachine = "sfn-statemachine"
    sns_topic = "sns-topic"
    sqs_queue = "sqs-queue"
    ssm_parameter = "ssm-parameter"
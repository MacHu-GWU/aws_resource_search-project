# -*- coding: utf-8 -*-

searchers_metadata = {
    "glue-database": {"mod": "glue", "var": "glue_database_searcher"},
    "glue-job": {"mod": "glue", "var": "glue_job_searcher"},
    "glue-jobrun": {"mod": "glue", "var": "glue_job_run_searcher"},
    "glue-table": {"mod": "glue", "var": "glue_table_searcher"},
    "iam-group": {"mod": "iam", "var": "iam_group_searcher"},
    "iam-role": {"mod": "iam", "var": "iam_role_searcher"},
    "s3-bucket": {"mod": "s3", "var": "s3_bucket_searcher"},
    "sfn-execution": {"mod": "sfn", "var": "sfn_execution_searcher"},
    "sfn-statemachine": {"mod": "sfn", "var": "sfn_state_machine_searcher"},
}

class SearcherEnum:
    glue_database = "glue-database"
    glue_job = "glue-job"
    glue_jobrun = "glue-jobrun"
    glue_table = "glue-table"
    iam_group = "iam-group"
    iam_role = "iam-role"
    s3_bucket = "s3-bucket"
    sfn_execution = "sfn-execution"
    sfn_statemachine = "sfn-statemachine"
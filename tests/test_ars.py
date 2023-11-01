# -*- coding: utf-8 -*-

from rich import print as rprint

from aws_resource_search.ars import ARS
from aws_resource_search.searchers import searchers_metadata, SearcherEnum
from aws_resource_search.logger import logger
from aws_resource_search.tests.fake_aws.api import FakeAws, guid, envs, rand_env


class TestARS(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        cls.setup_ars()
        cls.ars.clear_all_cache()

        if cls.bsm.aws_account_id != "123456789012":
            raise ValueError("This test only works with fake AWS account 123456789012")

        cls.create_all()

    def _test_ars(self):
        ars = self.ars

        assert ars.is_valid_resource_type(SearcherEnum.s3_bucket) is True
        assert ars.is_valid_resource_type("not-available") is False

    def _test_all(self):
        """
        这个方法用来测试 list resource 的时候无需任何额外参数的情况, 也就是简单情况.
        """
        resource_type_list = [
            # SearcherEnum.cloudformation_stack,
            # SearcherEnum.dynamodb_table,
            # SearcherEnum.ec2_instance,
            # SearcherEnum.ec2_securitygroup,
            # SearcherEnum.ec2_subnet,
            # SearcherEnum.ec2_vpc,
            # SearcherEnum.glue_crawler,
            # SearcherEnum.glue_database,
            # SearcherEnum.glue_job,
            # SearcherEnum.glue_jobrun, # we need to test it in another way
            # SearcherEnum.glue_table, # we need to test it in another way
            # SearcherEnum.iam_group,
            # SearcherEnum.iam_policy,
            # SearcherEnum.iam_role,
            # SearcherEnum.iam_user,
            # SearcherEnum.kms_alias,
            # SearcherEnum.lambda_function,
            # SearcherEnum.lambda_layer,
            # SearcherEnum.s3_bucket,
            # SearcherEnum.secretsmanager_secret,
            # SearcherEnum.sfn_execution,
            SearcherEnum.sfn_statemachine,
            # SearcherEnum.sns_topic,
            # SearcherEnum.sqs_queue,
            # SearcherEnum.ssm_parameter,
        ]

        ars = self.ars

        # ars.aws_console.sqs.get_queue(name_or_arn_or_url=123)
        for resource_type in resource_type_list:
            logger.ruler(f"start {resource_type!r}")
            searcher = ars.get_searcher(resource_type=resource_type)
            result = searcher.search(
                query=guid,
                refresh_data=True,
                simple_response=True,
                verbose=False,
            )
            # logger.info(result)
            for doc in result:
                logger.info(
                    f"id = {doc.id!r} "
                    f"| name = {doc.name!r} "
                    f"| url = {doc.get_console_url(ars.aws_console)}"
                )
                assert guid in doc.name
            logger.ruler(f"end {resource_type!r}")

    def test(self):
        print("")
        with logger.disabled(
            disable=True,  # no log,
            # disable=False,  # show log
        ):
            self._test_ars()
            self._test_all()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.ars", preview=False)

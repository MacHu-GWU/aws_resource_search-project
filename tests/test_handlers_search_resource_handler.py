# -*- coding: utf-8 -*-

from aws_resource_search.handlers.search_resource_handler import (
    search_resource,
    search_resource_under_partitioner,
)
from aws_resource_search.tests.fake_aws.utils import guid
from aws_resource_search.tests.fake_aws.main import FakeAws


class TestSearchResourceHandler(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        cls.setup_ars()
        cls.setup_ui()
        cls.create_s3_bucket()
        cls.create_state_machines()

    def test_search_resource(self):
        items = search_resource(
            ui=self.ui,
            resource_type="s3-bucket",
            query=guid,
            skip_ui=True,
        )
        assert len(items) > 1
        for item in items:
            assert guid in item.get_name()

        items = search_resource(
            ui=self.ui,
            resource_type="s3-bucket",
            query="invalidresource",
            skip_ui=True,
        )
        assert len(items) == 1

        items = search_resource(
            ui=self.ui,
            resource_type="s3-bucket",
            query=f"{guid}!~",
            skip_ui=True,
        )
        for item in items:
            assert guid in item.get_name()

    def test_search_resource_under_partitioner(self):
        sm_items = search_resource(
            ui=self.ui,
            resource_type="sfn-state-machine",
            query=guid,
            skip_ui=True,
        )
        for sm_item in sm_items:
            items = search_resource_under_partitioner(
                ui=self.ui,
                resource_type="sfn-state-machine-execution",
                partitioner_resource_type=f"sfn-state-machine",
                query=f"{sm_item.get_name()}@{guid}",
                skip_ui=True,
            )
            # this won't work because moto doesn't handle create_state_machine properly
            # the list_executions API doesn't work.
            # for item in items:
            #     assert guid in item.get_name()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(
        __file__,
        "aws_resource_search.handlers.search_resource_handler",
        preview=False,
    )

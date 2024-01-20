# -*- coding: utf-8 -*-

from aws_resource_search.tests.fake_aws.api import FakeAws


class TestARSDef(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        cls.setup_ars()

    def _test_all_resource_types(self):
        _ = self.ars.all_resource_types()

    def _test_is_valid_resource_type(self):
        assert self.ars.is_valid_resource_type("s3-bucket") is True
        assert self.ars.is_valid_resource_type("invalid") is False

    def _test_set_profile(self):
        self.ars.set_profile()

    def test(self):
        self._test_all_resource_types()
        self._test_is_valid_resource_type()
        self._test_set_profile()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.ars_def", preview=False)

# -*- coding: utf-8 -*-

from aws_resource_search.tests.fake_aws.api import FakeAws


class TestApi(FakeAws):
    @classmethod
    def setup_class_post_hook(cls):
        cls.setup_ars()

    def test(self):
        import aws_resource_search.api as aws_resource_search

        _ = aws_resource_search.format_shortcut
        _ = aws_resource_search.highlight_text
        _ = aws_resource_search.format_resource_type
        _ = aws_resource_search.format_key
        _ = aws_resource_search.format_value
        _ = aws_resource_search.format_key_value
        _ = aws_resource_search.ShortcutEnum
        _ = aws_resource_search.SUBTITLE
        _ = aws_resource_search.SHORT_SUBTITLE
        _ = aws_resource_search.SearcherEnum
        _ = aws_resource_search.T_RESULT_DATA
        _ = aws_resource_search.ResourceIterproxy
        _ = aws_resource_search.ResultPath
        _ = aws_resource_search.list_resources
        _ = aws_resource_search.extract_tags
        _ = aws_resource_search.BaseArsDocument
        _ = aws_resource_search.T_ARS_DOCUMENT
        _ = aws_resource_search.ResourceTypeDocument
        _ = aws_resource_search.get_utc_now
        _ = aws_resource_search.to_human_readable_elapsed
        _ = aws_resource_search.to_utc_dt
        _ = aws_resource_search.SIMPLE_DT_FMT
        _ = aws_resource_search.to_simple_dt_fmt
        _ = aws_resource_search.to_iso_dt_fmt
        _ = aws_resource_search.get_none_or_default
        _ = aws_resource_search.get_description
        _ = aws_resource_search.get_datetime
        _ = aws_resource_search.get_datetime_simple_fmt
        _ = aws_resource_search.get_datetime_iso_fmt
        _ = aws_resource_search.ResourceDocument
        _ = aws_resource_search.T_ARS_RESOURCE_DOCUMENT
        _ = aws_resource_search.BaseArsItem
        _ = aws_resource_search.T_ARS_ITEM
        _ = aws_resource_search.DetailItem
        _ = aws_resource_search.ExceptionItem
        _ = aws_resource_search.FileItem
        _ = aws_resource_search.InfoItem
        _ = aws_resource_search.UrlItem
        _ = aws_resource_search.AwsResourceTypeItem
        _ = aws_resource_search.AwsResourceItem
        _ = aws_resource_search.SetAwsProfileItem
        _ = aws_resource_search.ShowAwsInfoItem
        _ = aws_resource_search.preprocess_query
        _ = aws_resource_search.BaseSearcher
        _ = aws_resource_search.T_SEARCHER
        _ = aws_resource_search.config
        _ = aws_resource_search.ARS
        _ = aws_resource_search.search_aws_profile_handler
        _ = aws_resource_search.search_resource_type_handler
        _ = aws_resource_search.search_resource_handler
        _ = aws_resource_search.show_aws_info_handler
        _ = aws_resource_search.UI
        _ = aws_resource_search.handler


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.api", preview=False)

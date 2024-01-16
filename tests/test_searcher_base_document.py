# -*- coding: utf-8 -*-

import dataclasses

import pytest

import json
from datetime import datetime, timezone

import botocore.exceptions

import sayt.api as sayt
from aws_resource_search.searcher.base_document import (
    get_utc_now,
    to_human_readable_elapsed,
    to_utc_dt,
    to_simple_dt_fmt,
    to_iso_dt_fmt,
    get_none_or_default,
    get_description,
    get_datetime_iso_fmt,
    get_datetime_simple_fmt,
    BaseDocument,
)


def test_human_readable_elapsed():
    assert to_human_readable_elapsed(15) == "15 sec"
    assert to_human_readable_elapsed(60) == "1 min"
    assert to_human_readable_elapsed(90) == "1 min 30 sec"
    assert to_human_readable_elapsed(3600) == "1 hour"
    assert to_human_readable_elapsed(3725) == "1 hour 2.1 min"
    assert to_human_readable_elapsed(86400) == "1 day"
    assert to_human_readable_elapsed(93900) == "1 day 2.1 hour"


def test_to_utc_dt():
    assert to_utc_dt(datetime.utcnow()).tzinfo == timezone.utc


def test_to_simple_dt_fmt():
    assert "+" not in to_simple_dt_fmt(get_utc_now())


def test_to_iso_dt_fmt():
    assert "+00:00" in to_iso_dt_fmt(get_utc_now())


def test_get_none_or_default():
    data = {"a": 1, "b": {"c": 3}}
    assert get_none_or_default(data, "a") == 1
    assert get_none_or_default(data, "d") is None
    assert get_none_or_default(data, "d", "hello") == "hello"
    assert get_none_or_default(data, "b.c") == 3
    assert get_none_or_default(data, "b.d") is None
    assert get_none_or_default(data, "b.d", "hello") == "hello"
    assert get_none_or_default(data, "c.e") is None
    assert get_none_or_default(data, "c.e", "hello") == "hello"


def test_get_datetime_simple_fmt():
    assert get_datetime_simple_fmt({}, "time") == "No datetime"
    data = {"time": datetime(2000, 1, 1)}
    assert get_datetime_simple_fmt(data, "time") == "2000-01-01 00:00:00"


def test_get_datetime_iso_fmt():
    assert get_datetime_iso_fmt({}, "time") == "No datetime"
    data = {"time": datetime(2000, 1, 1)}
    assert get_datetime_iso_fmt(data, "time") == "2000-01-01T00:00:00+00:00"


@dataclasses.dataclass
class S3Bucket(BaseDocument):
    @classmethod
    def from_resource(
        cls,
        resource,
        bsm,
        boto_kwargs,
    ):
        return cls(
            raw_data=resource,
            id=resource["Name"],
            name=resource["Name"],
        )

    @property
    def title(self) -> str:
        return f"bucket = {self.name}"

    @property
    def arn(self) -> str:
        return f"arn:aws:s3:::{self.name}"

    def get_console_url(self, console) -> str:
        return console.s3.get_console_url(bucket=self.name)


class TestDocument:
    def _test_properties_methods(self):
        doc = BaseDocument(raw_data={}, id="test", name="test")
        with pytest.raises(NotImplementedError):
            _ = doc.title
        _ = doc.subtitle
        _ = doc.short_subtitle
        _ = doc.autocomplete
        with pytest.raises(NotImplementedError):
            _ = doc.arn
        with pytest.raises(NotImplementedError):
            _ = doc.get_console_url(console=None)
        # with pytest.raises(NotImplementedError):
        #     _ = doc.get_details(ars=None)
        # assert doc.get_initial_detail_items(ars=None) == []

        s3_bucket = S3Bucket.from_resource(
            resource={"Name": "test-bucket", "CreationDate": datetime(2021, 1, 1)},
            bsm=None,
            boto_kwargs=None,
        )
        _ = s3_bucket.title
        _ = s3_bucket.subtitle
        _ = s3_bucket.short_subtitle
        _ = s3_bucket.autocomplete
        _ = s3_bucket.uid
        _ = s3_bucket.arn

    def _test_enrich_details(self):
        detail_items = []
        with BaseDocument.enrich_details(detail_items):
            detail_items.append("hello")
            raise botocore.exceptions.ClientError(
                error_response={}, operation_name="test"
            )
            detail_items.append("word")
        assert len(detail_items) == 2
        assert detail_items[0] == "hello"
        assert "❗" in detail_items[1].title

    def _test_one_line(self):
        assert BaseDocument.one_line("hello") == "hello"
        assert BaseDocument.one_line("hello\nword") == "hello ..."
        assert (
            BaseDocument.one_line(json.dumps(dict(a=1, b=2), indent=4))
            == '{"a": 1, "b": 2}'
        )
        assert BaseDocument.one_line("") == "NA"
        assert BaseDocument.one_line(None, "Not available") == "Not available"
        assert BaseDocument.one_line(dict(a=1, b=2)) == '{"a": 1, "b": 2}'

    def _test_to_searcher_fields(self):
        @dataclasses.dataclass
        class DummyS3Bucket(BaseDocument):
            arn: str = dataclasses.field(
                metadata={"field": sayt.StoredField(name="arn")}
            )

        search_fields = DummyS3Bucket.to_searcher_fields()
        assert search_fields[3].name == "arn"
        assert isinstance(search_fields[3], sayt.StoredField)

        @dataclasses.dataclass
        class WrongResource1(BaseDocument):
            arn: str = dataclasses.field()

        with pytest.raises(KeyError):
            WrongResource1.to_searcher_fields()

        @dataclasses.dataclass
        class WrongResource2(BaseDocument):
            arn: str = dataclasses.field(metadata={"field": 123})

        with pytest.raises(TypeError):
            WrongResource2.to_searcher_fields()

        @dataclasses.dataclass
        class WrongResource3(BaseDocument):
            arn: str = dataclasses.field(
                metadata={"field": sayt.StoredField(name="bucket_arn")}
            )

        with pytest.raises(ValueError):
            WrongResource3.to_searcher_fields()

    def test(self):
        self._test_properties_methods()
        # self._test_enrich_details()
        # self._test_one_line()
        self._test_to_searcher_fields()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.searcher.base_document", preview=False)

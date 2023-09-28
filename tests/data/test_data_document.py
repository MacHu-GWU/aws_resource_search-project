# -*- coding: utf-8 -*-

from aws_resource_search.data.document import (
    FieldTypeEnum,
    Field,
    parse_doc_json_node,
    extract_document,
)

from rich import print as rprint


class Test:
    def _test_Field(self):
        field = Field(name="id", type=FieldTypeEnum.Id.value, token="$_res.instance_id")
        assert field.to_dict() == {
            "name": "id",
            "type": "Id",
            "token": "$_res.instance_id",
            "kwargs": {},
        }
        assert (
            Field.from_dict(
                {"name": "id", "type": "Id", "token": "$_res.instance_id", "kwargs": {}}
            )
            == field
        )

        value = field.evaluate({"_res": {"instance_id": "i-1a2b"}, "_out": {}})
        assert value == "i-1a2b"

        field._to_sayt_field()

    def _test_extract_document(self):
        data = extract_document(
            document=parse_doc_json_node(
                {
                    "id": {"type": "Id", "token": "$_res.instance_id"},
                }
            ),
            output={"_res": {"instance_id": "i-1a2b"}, "_out": {}},
        )
        assert data == {
            "id": "i-1a2b",
            "raw_data": {"_res": {"instance_id": "i-1a2b"}, "_out": {}},
        }

    def test(self):
        self._test_Field()
        self._test_extract_document()


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.data.document", preview=False)

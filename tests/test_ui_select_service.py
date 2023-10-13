# -*- coding: utf-8 -*-

import afwf_shell.api as afwf_shell
from aws_resource_search.ui import (
    handler,
    ars,
)
from rich import print as rprint

service_id_and_resource_type_pairs = ars._service_id_and_resource_type_pairs()
ui = afwf_shell.UI(handler=handler)


def test():
    items = handler(query=" ", ui=ui)
    assert len(items) == len(service_id_and_resource_type_pairs)

    items = handler(query="ec2 inst", ui=ui)
    assert items[0].uid == "ec2-instance"

    items = handler(query="ec2 inst: something", ui=ui)
    assert items[0].uid == "ec2-instance"


if __name__ == "__main__":
    from aws_resource_search.tests.helper import run_cov_test

    run_cov_test(__file__, "aws_resource_search.ui", preview=False)

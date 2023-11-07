Developer Guide - How It Works Under he Hood
==============================================================================


How does the Search Work
------------------------------------------------------------------------------
Let's consider an example in which we search for an EC2 instance using its instance ID, name tag, state, VPC ID, or subnet ID.

.. code-block::

    (Query): ec2-instance:
    [x] name_tag = jump-box
          🔴️ stopped | i-1a2b3c4d | t2.micro | vpc = vpc-1a2b3c4d, 🌐 Enter, 📋 Ctrl A, 🔗 Ctrl U, 👀 Ctrl P.
    [ ] name_tag = dev-machine
          🔴️ stopped | i-5e6f7g8h | t2.large | vpc = vpc-1a2b3c4d, 🌐 Enter, 📋 Ctrl A, 🔗 Ctrl U, 👀 Ctrl P.

**Download and index data**

When you entered ``(Query): ec2-instance:``, what happens are:

1. Check whether the data has already been indexed. If it has not been indexed, proceed to step 2. If indexing has already been completed, proceed to step 3."
2. Call Boto3 `ec2.describe_instances <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/paginator/DescribeInstances.html>`_ to get the data and index them. Different AWS resources use different boto3 API.
3. Parse user query and search the indexed data. If user query is empty, return all data.
4. Render the return data in the UI.

**Define AWS resource index schema**

Different AWS resources has different index schema. All AWS resources has two default searchable fields, ``id`` and ``arn``. For example, the index schema for EC2 instance is:

1. the ``id`` field is the unique identifier of the document. and it is also a searchable ``IdField``. this field haves higher weight (in field_boost).
2. the ``name`` field is a human-firendly name, and it is also an n-gram searchable ``NgramWordsField``. the default setting is that the result is ordered by name in ascending order (in name_sortable and name_ascending).

Some AWS resources may need more searchable fields. For example, EC2 should be able to search by ``state``, ``vpc_id``, and ``subnet_id``. In this case, you can define more searchable fields in the searcher object.

Below are the `source code for EC2 searcher <../_modules/aws_resource_search/res/ec2.html#Ec2InstanceSearcher>`_

.. code-block:: python

    ec2_instance_searcher = Ec2InstanceSearcher(
        # list resources
        service="ec2",
        method="describe_instances",
        is_paginator=True,
        default_boto_kwargs={"PaginationConfig": {"MaxItems": 9999, "PageSize": 1000}},
        ...
        fields=res_lib.define_fields(
            # fmt: off
            fields=[
                res_lib.sayt.NgramWordsField(name="state", minsize=2, maxsize=4, stored=True),
                res_lib.sayt.NgramWordsField(name="vpc_id", minsize=2, maxsize=4, stored=True),
                res_lib.sayt.NgramWordsField(name="subnet_id", minsize=2, maxsize=4, stored=True),
                res_lib.sayt.NgramWordsField(name="id_ng", minsize=2, maxsize=4, stored=True),
                res_lib.sayt.StoredField(name="inst_arn"),
            ],
            # fmt: on
        ),
        cache_expire=24 * 60 * 60,
        ...
    )

**Query Parser**

The user's query is automatically parsed and transformed into tokens by removing all delimiter characters. Additionally, it enables fuzzy matching to accommodate potential typographical errors. Multiple tokens are combined using a logical AND operation, requiring matched documents to satisfy all tokens.

For example, the query ``dev-box`` will be parsed as logic AND of:

- ``de`` or ``ev`` or ``dev``
- ``bo`` or ``ox`` or ``box``
- ``dev~1`` (fuzzy match on edit distance 1)
- ``box~`` (fuzzy match on edit distance 1)


How does the User Action Work
------------------------------------------------------------------------------
``🌐 Enter, 📋 Ctrl A, 🔗 Ctrl U, 👀 Ctrl P.``. These are **user action** that you can interact with the selected AWS resources.

``aws_resource_search`` implements the corresponduing action in the following methods:

- :meth:`~aws_resource_search.ui.search_resource.AwsResourceItem.enter_handler`: use ``start`` command (on windows) or ``open`` command (on Mac or Linux) to open URL in default browser.
- :meth:`~aws_resource_search.ui.search_resource.AwsResourceItem.ctrl_a_handler`: use `pyperclip <https://pypi.org/project/pyperclip/>`_ to copy ARN to clipboard.
- :meth:`~aws_resource_search.ui.search_resource.AwsResourceItem.ctrl_u_handler`: use `pyperclip <https://pypi.org/project/pyperclip/>`_ to copy URL to clipboard.
- :meth:`~aws_resource_search.ui.search_resource.AwsResourceItem.ctrl_p_handler`: enter a sub session to display AWS resource details.

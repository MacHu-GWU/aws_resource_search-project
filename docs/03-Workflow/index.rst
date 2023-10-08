Test
==============================================================================




Call Boto3 API to get the Data
------------------------------------------------------------------------------
从在 API 设计上, 当用户用包含了 AWS Credential 的 ``boto_session_manager.BotoSesManager`` 对象初始化了一个 AWS Resource Search (ARS) 对象以后, 就可以调用对应的 service id 和 resource type 的方法来进行搜索了. 下面的代码展示了如何用 ``my_aws_profile`` 这一 AWS CLI Profile 来创建 ``ARS`` 对象, 然后搜索所有的 S3 Bucket.

.. code-block:: python

    from boto_session_manager import BotoSesManager
    from aws_resource_search.api import ARS

    bsm = BotoSesManager(profile_name="my_aws_profile")
    ars = ARS(bsm=bsm)
    ars.s3_bucket.search("*")

当用户调用 ``search`` 方法的时候, ARS 会自动检查看看 S3 Bucket 的数据以前是否下载过并已经做好了 Index. 这个检查是通过检查缓存来进行的, 这个缓存会在一定时间后自动过期. 用户也可以进行手动刷新. 详细的机制我们之后再介绍. 如果没有找到, 那么就会运行 boto3 API 来获取数据.

`s3_client.list_buckets <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_buckets.html>`_

1. Request: 调用 boto3 API, 获取数据
2. Enrich: 对数据进行处理, 丰富数据
3. Document: 对数据进行文档化, 生成文档
API Request Constructor:

.. code-block:: python

    {
        "s3": {
            "bucket": {
                "request": {
                    "method": "list_buckets",
                    "is_paginator": false,
                    "items_path": "$Buckets || `[]`",
                }
            }
        }
    }

API Response:

.. code-block:: python

    {
        'Buckets': [
            {
                'Name': 'string',
                'CreationDate': datetime(2015, 1, 1)
            },
        ],
        'Owner': {
            'DisplayName': 'string',
            'ID': 'string'
        }
    }



                "method": "list_buckets",
                "is_paginator": false,
                "items_path": "$Buckets || `[]`",

Item:

.. code-block:: python

    {
        'Name': 'string',
        'CreationDate': datetime(2015, 1, 1)
    }

Result Selector:

.. code-block:: python

    {
        "arn": {
            "type": "str",
            "value": {
                "type": "sub",
                "kwargs": {
                    "template": "arn:aws:s3:::{bucket}",
                    "params": {
                        "bucket": "$Name"
                    }
                }
            }
        },
    }

.. code-block:: javascript

    {
        "req": {},
        "out": {},
        "doc": {},
        "url": {}
    }


- req (Request):
- out (Output):
- doc (Document):
- url (Console Url):

.. code-block:: javascript

    {
        "ec2-instance": {
            "req": {
                "method": "describe_instances",
                "kwargs": {
                    "PaginationConfig": {
                        "MaxItems": 9999,
                        "PageSize": 1000
                    }
                },
                "cache_key": [
                    "$Filters[?Name=='vpc-id'].Values[] || `[]` | join(', ', sort(@))"
                ],
                "is_paginator": true,
                "result_path": "$Reservations[].Instances[] || `[]`"
            },
            "out": {
                "arn": {
                    "type": "str",
                    "token": {
                        "type": "Token::Sub",
                        "kwargs": {
                            "template": "arn:aws:ec2:{aws_region}:{aws_account_id}:instance/{instance_id}",
                            "params": {
                                "instance_id": "$_res.InstanceId",
                                "aws_region": "$_ctx.AWS_REGION",
                                "aws_account_id": "$_ctx.AWS_ACCOUNT_ID"
                            }
                        }
                    }
                },
                "title": {
                    "type": "str",
                    "token": "$_res.Tags[?Key=='Name'].Value | [0] || 'No instance name'"
                },
                "subtitle": {
                    "type": "str",
                    "token": {
                        "type": "Token::Sub",
                        "kwargs": {
                            "template": "{state_icon} {state} | {inst_id} | {inst_type}",
                            "params": {
                                "state": "$_res.State.Name",
                                "state_icon": {
                                    "type": "Token::Map",
                                    "kwargs": {
                                        "key": "$_res.State.Name",
                                        "mapper": {
                                            "pending": "🟡",
                                            "running": "🟢",
                                            "shutting-down": "🟤",
                                            "terminated": "⚫",
                                            "stopping": "🟠",
                                            "stopped": "🔴️"
                                        }
                                    }
                                },
                                "inst_id": "$_res.InstanceId",
                                "inst_type": "$_res.InstanceType"
                            }
                        }
                    }
                },
                "arg": {
                    "type": "str",
                    "token": "$_res.InstanceId"
                },
                "autocomplete": {
                    "type": "str",
                    "token": "$_res.InstanceId"
                }
            },
            "doc": {
                "id": {
                    "type": "Id",
                    "token": "$_res.InstanceId",
                    "kwargs": {
                        "stored": true,
                        "field_boost": 10
                    }
                },
                "inst_id": {
                    "type": "Ngram",
                    "token": "$_res.InstanceId",
                    "kwargs": {
                        "stored": true
                    }
                },
                "name": {
                    "type": "NgramWords",
                    "token": "$_res.Tags[?Key=='Name'].Value | [0] || 'No instance name'",
                    "kwargs": {
                        "stored": true
                    }
                }
            },
            "url": {
                "method": "get_instance",
                "kwargs": {
                    "instance_id_or_arn": "$raw_data._res.InstanceId"
                }
            }
        },
        ..., # other services
    }
Developer Guide
==============================================================================


I want to change ...
------------------------------------------------------------------------------


Change the Title, Subtitle, auto complete, URL of AWS Resource Item in the UI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For example, you want to change the title, subtitle, auto complete text or the URL for AWS S3 Bucket.

1. Locate the corresponding :mod:`~aws_resource_search.res.s3` module.
2. Locate the :class:`~aws_resource_search.res.s3.S3Bucket` class. It defines how can you get data from boto3 ``s3_client.list_buckets`` API call.
3. Update the :meth:`~aws_resource_search.res.s3.S3Bucket.title`, ``subtitle``, ``autocomplete`` and ``get_console_url`` attributes.


Change the User Action behavior when tap Enter, Ctrl A, etc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For example, you want to change the default behavior of user action (``Enter`` is "Open AWS console url in browser", ``Ctrl + A`` "is Copy ARN to clipboard", ``Ctrl + U`` is "Copy AWS console url to clipboard.", ``Ctrl + P`` is "View details in a sub session. You can tap 'F1' to exit the sub session.").

1. Locate the corresponding :mod:`~aws_resource_search.ui.search_resource` module.
2. Locate the :mod:`~aws_resource_search.ui.search_resource.AwsResourceItem` class.
3. Update the corresponding :meth:`~aws_resource_search.ui.search_resource.AwsResourceItem.enter_handler`, :meth:`~aws_resource_search.ui.search_resource.AwsResourceItem.ctrl_a_handler`, :meth:`~aws_resource_search.ui.search_resource.AwsResourceItem.ctrl_u_handler`, :meth:`~aws_resource_search.ui.search_resource.AwsResourceItem.ctrl_p_handler` method. **Note that this will change the behavior for ALL AWS resources**. If you only want to change for one AWS resource, you can subclass this.

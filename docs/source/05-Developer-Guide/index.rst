Developer Guide
==============================================================================


I want to change ...
------------------------------------------------------------------------------


Change the Title, Subtitle, auto complete, URL of AWS Resource Item in the UI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For example, you want to change the title, subtitle, auto complete text or the URL for AWS S3 Bucket.

1. Locate the corresponding ``aws_resource_search/res/s3.py`` file.
2. Locate the ``S3Bucket`` class.
3. Update the ``title``, ``subtitle``, ``autocomplete`` and ``url`` attributes.


Change the User Action behavior when tap Enter, Ctrl A, etc
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Locate the corresponding ``aws_resource_search/ui/search_resource.py.py`` file.
2. Locate the ``AwsResourceItem`` class.

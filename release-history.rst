.. _release_history:

Release and Version History
==============================================================================


Backlog (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.6.1 (2024-01-20)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add config system so that user can configure ARS by editing the ``~/.aws_resource_search/config.json`` file.
- add ``!{`` command to view and edit the json file.
- allow user to jump to list aws resources view in AWS console by tapping 'Enter' key in aws resource type search view.
- allow fuzzy search with 1 character edit distance.

**Minor Improvements**

- refactor the entire code base, make it more modular and testable.

**Bugfixes**

- fix a bug that when switch to another aws profile, the ``AWSConsole`` object didn't get updated.


0.5.1 (2024-01-14)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add support for:
    - ecr-repository
    - ecr-repository-image
    - ecs-cluster
    - ecs-task-run
    - ecs-task-definition-family
- Allow user to use ``!@`` to switch between aws profile without leaving the interactive session.
- Allow user to use ``!?`` to show AWS account info for the current profile.


0.4.1 (2023-11-07)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add support for:
    - lambda-alias
    - rds-dbinstance
    - rds-dbcluster

**Minor Improvements**

- Add lambda layer information in lambda function details.
- Allow tap 'Enter' to open url in detail view for most of detail items.
- Greatly refactor the source code to make it more maintainable.
- Update document.

**Bugfixes**

- fix a bug that we should call api to get latest data for mutable resources.
- fix a bug that we raise boto3 session validation error when we don't really need it in some CLI command like ``ars --version``.


0.3.1 (2023-11-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add ``ars -h`` to show help message.
- Add ``ars which`` command to show the current AWS account and region information.
- Removed ``ars-set-profile``, add ``ars set-profile`` command instead.
- Add ``ars clear`` command to clear all cache and index.

**Minor Improvements**

- Improved the message when the boto3 list resources API call returns an empty list.
- Improved the message when searcher returns no match.
- Improved the autocomplete when the searcher returns no match, so user can easily re-enter the query.

**Bugfixes**

- Fix a bug that codebuild-jobrun may fail if there's no build in the project.

**Miscellaneous**

- Improve the documentation.


0.2.1 (2023-11-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add support for:
    - codebuild-project
    - codebuild-job-run
    - codepipeline-pipeline

**Minor Improvements**

- Sort execution-liked aws resource by start time in descending order by default.
- Print text content instead of copying to clipboard when the clipboard is not available in a remote shell system (like ssh session)
- Print url instead of open in web browser when the web browser is not available in a remote shell system (like ssh session)

**Bugfixes**

- Fix a bug that it has to tap 'Ctrl C' multiple time to quit from sub session.


0.1.3 (2023-11-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- Fix a bug that Python3.7 cannot import TypedDict.


0.1.2 (2023-11-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Miscellaneous**

- Add support for Python3.7 for backward compatibility.


0.1.1 (2023-11-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First release.

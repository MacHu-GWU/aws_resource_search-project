.. _release_history:

Release and Version History
==============================================================================


Backlog (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add a JSON config system for this app.
- add ``ars config`` command to view and edit the json file.

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


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
    - codebuild-jobrun
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

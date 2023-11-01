
.. image:: https://readthedocs.org/projects/ars/badge/?version=latest
    :target: https://ars.readthedocs.io/index.html
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/aws_resource_search-project/workflows/CI/badge.svg
    :target: https://github.com/MacHu-GWU/aws_resource_search-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/aws_resource_search-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/aws_resource_search-project

.. image:: https://img.shields.io/pypi/v/aws_resource_search.svg
    :target: https://pypi.python.org/pypi/aws_resource_search

.. image:: https://img.shields.io/pypi/l/aws_resource_search.svg
    :target: https://pypi.python.org/pypi/aws_resource_search

.. image:: https://img.shields.io/pypi/pyversions/aws_resource_search.svg
    :target: https://pypi.python.org/pypi/aws_resource_search

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/aws_resource_search-project

------


.. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://ars.readthedocs.io/index.html

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://aws_resource_search.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
    :target: https://aws_resource_search.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/aws_resource_search-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/aws_resource_search-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/aws_resource_search-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/aws_resource_search#files


Welcome to ``aws_resource_search`` Documentation
==============================================================================
AWS Resource Search (ARS) is a terminal application that can search AWS resource interactively.

1. It is using advanced index technique that support full-text-search (any word, doesn't have to be prefix or suffix), fuzzy search (spelling mistake is OK), ngram-search (series of n adjacent characters is OK).
2. It support query caching out-of-the-box that it is blazing fast even you have thousands of AWS resources like IAM role, Lambda Functions, CloudFormation stacks, etc.
3. It is just a Python library, so that you just need to ``pip install aws_resource_search`` and you don't need to setup any database or search or install any software.

The open source community version can search one AWS Account and one AWS region at a time, you can use ARS to switch between different AWS accounts before searching. The enterprise version can search multiple AWS account and AWS regions in a aggregated view, now the enterprise version is on beta and plan to become generally available on early 2024..


Demo
------------------------------------------------------------------------------
Search S3 Bucket.

.. image:: https://asciinema.org/a/618423.svg
    https://asciinema.org/a/618423

Search StepFunction execution, which is a child resource of StepFunction state machine.

.. image:: https://asciinema.org/a/618428.svg
    https://asciinema.org/a/618428


.. _install:

Install
------------------------------------------------------------------------------

``aws_resource_search`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install aws_resource_search

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade aws_resource_search
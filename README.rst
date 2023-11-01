
.. image:: https://readthedocs.org/projects/ars/badge/?version=latest
    :target: https://ars.readthedocs.io/en/latest/index.html
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
    :target: https://ars.readthedocs.io/en/latest/index.html

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://ars.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
    :target: https://ars.readthedocs.io/en/latest/py-modindex.html

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
.. image:: https://ars.readthedocs.io/en/latest/_static/aws_resource_search-logo.png
    :target: https://ars.readthedocs.io/en/latest/index.html
    :align: center
    :width: 256px

📙 `Full Documentation HERE <https://ars.readthedocs.io/en/latest/index.html>`_

**AWS Resource Search (ARS)** is a terminal application that enables interactive searches for AWS resources. It is a mini AWS console in your terminal or shell environment.

It utilizes advanced indexing techniques that support ``full-text search`` (any word, no longer restricted to prefix or suffix matching), ``fuzzy search`` (tolerating spelling mistakes), and ``n-gram`` search (allowing matching of series of n adjacent characters).

ARS comes with built-in query caching, ensuring ``blazing-fast performance`` even when dealing with a large number of AWS resources such as IAM roles, Lambda Functions, CloudFormation stacks, and more.

As a Python library, installation is as simple as running ``pip install aws_resource_search``. There's no need to set up databases, additional search tools, or install any other software.

The data stays on your laptop, there's no remote server involved.

The **open-source Community Edition** of ARS allows searching within a single AWS Account and one AWS region at a time. You can switch between different AWS accounts before conducting your searches. On the other hand, the **Enterprise Edition** of ARS offers the capability to search across multiple AWS accounts and AWS regions, providing an aggregated view. Currently, the enterprise version is in beta and is expected to become generally available in early 2024."


Demo
------------------------------------------------------------------------------
Search S3 Bucket.

.. image:: https://asciinema.org/a/618423.svg
    :target: https://asciinema.org/a/618423

Search StepFunction execution, which is a child resource of StepFunction state machine.

.. image:: https://asciinema.org/a/618428.svg
    :target: https://asciinema.org/a/618428


.. _install:

Install
------------------------------------------------------------------------------

``aws_resource_search`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install aws_resource_search

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade aws_resource_search
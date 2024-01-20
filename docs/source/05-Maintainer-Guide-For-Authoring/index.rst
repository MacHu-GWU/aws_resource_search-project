Maintainer Guide for Authoring
==============================================================================
This document is designed for myself to remember how this software designed.


前言
------------------------------------------------------------------------------
一般有两种描述一个系统的内部设计的方式:

1. 从底层模块出发, 一点点的构建起系统的各个模块, 并最后串联成一个系统. 这是一种在设计一个系统时用到的思维.
2. 从最终的用户界面触发, 一点点往下深挖, 看实际底层按照顺序调用了哪些模块. 这是一种在理解一个系统时用到的思维.

这篇文档的主要目的是方便我自己在过了一段时间后回来维护这个项目时理解这个系统用的, 所以我会按照 #2 的思路来写这篇文档.


CLI 命令行初探
------------------------------------------------------------------------------
当你在命令行输入 ``ars`` 的时候, 就会调用 :func:`aws_resource_search.cli.main.run` 这个函数. 由于你没有输入任何 subcommand 以及参数, 所以它会调用 :meth:`aws_resource_search.cli.ArsCli.__call__` 这个方法. 这两个函数都是位于 :mod:`aws_resource_search.cli` 这个模块中的, 是负责 CLI 的接口的用的, 并不涉及具体业务逻辑. 而你看 ``__call__`` 这个方法就知道, 里面会调用 :func:`aws_resource_search.ui_init.run_ui` 这个函数. 这个函数是位于 :mod:`aws_resource_search.ui_init` 下的, 属于 UI 的核心逻辑的入口函数. 而 CLI 函数只是对这个函数的初探.


UI Event Loop
------------------------------------------------------------------------------
UI 的入口函数 :func:`aws_resource_search.ui_init.run_ui` 里面的内容和恩简单, 就是实例化一个 :class:`aws_resource_search.ui_def.UI` 对象, 然后进入 event loop. 对于 UI 来说, 你每按下一个按键, 都会调用一个函数来处理你的输入, 然后重新渲染整个界面. 这个用于处理输入的函数就是 :func:`aws_resource_search.ui_def.handler`


UI Handler
------------------------------------------------------------------------------
UI 的函数是用来处理

如何支持更多的 AWS 服务和资源
------------------------------------------------------------------------------
本节主要介绍如果你发现这个项目不支持你想要的 AWS 服务或者资源, 你应该如何去添加它.

1. 首先到 `aws_resource_search/code/searcher_enum.json <https://github.com/MacHu-GWU/aws_resource_search-project/blob/main/aws_resource_search/code/searcher_enum.json>`_ 仿照已经支持的 AWS Resource, 添加你要支持的 AWS Resource 的类型. 其中 ``description`` 是给人类看的一句话介绍, 一般是 AWS Document 官网首页的第一句话. 而 ``ngram`` 则是额外的用于搜索 ngram 搜索的关键字, 你可以把人类在想搜这个资源时能联想到的各种词汇的全称和缩写都放在这里.

.. dropdown:: aws_resource_search/code/searcher_enum.json

    .. literalinclude:: ../../../aws_resource_search/code/searcher_enum.json
       :language: python
       :linenos:

2. 然后到 `aws_resource_search/res/ <https://github.com/MacHu-GWU/aws_resource_search-project/tree/main/aws_resource_search/res>`_ 下, 找一个跟你要支持的服务比较相近的服务作为模版, copy paste 创建一个新的模块. 模块的名字要跟 AWS Service 对应上. 然后参考其他的模块实现这个搜索器.
3. 运行 `scripts/code_work.py <https://github.com/MacHu-GWU/aws_resource_search-project/blob/main/scripts/code_work.py>`_, 自动更新其他的 enum 模块, 数据, 和代码.
4. 如果你这个 resource 是一个先要搜索 parent resource, 然后才能搜的 sub resource, 你还要到 `aws_resource_search/ui/search_patterns.py <https://github.com/MacHu-GWU/aws_resource_search-project/blob/main/aws_resource_search/ars_search_patterns.py#L38>`_ 模块中更新 `ArsSearchPatternsMixin.get_search_patterns` 这个函数中定义的映射关系.

.. dropdown:: aws_resource_search/ars_search_patterns.py

    .. literalinclude:: ../../../aws_resource_search/ars_search_patterns.py
       :language: python
       :linenos:

5. 为了验证你的实现是否正确, 你需要到 `aws_resource_search/tests/fake_aws/ <https://github.com/MacHu-GWU/aws_resource_search-project/tree/main/aws_resource_search/tests/fake_aws>`_ 目录下创建 mock AWS resource 的模块, 你可以在里面找和你的 Resource 类似的模块作为参考.
6. 然后到 `aws_resource_search/tests/fake_aws/main.py <https://github.com/MacHu-GWU/aws_resource_search-project/blob/main/aws_resource_search/tests/fake_aws/main.py#L24>`_ 模块中更新 ``mock_list`` 中你要 mock 的列表, 以及更新 ``def create_all(self)`` 中的逻辑, 把创建你刚实现的 Resource 的逻辑加进去.
7. 然后你就可以用 ``pyops cov`` 命令, 或者手动运行 `tests/test_ars_init.py <https://github.com/MacHu-GWU/aws_resource_search-project/blob/main/tests/test_ars_init.py>`_ 单元测试来自动 mock 所有支持的 AWS 资源并尝试进行搜索了.


.. _what-is-searcher:

What is Searcher
------------------------------------------------------------------------------
我们这个 App 的核心功能就是搜索 AWS Resource. 而 AWS Resource 有很多种不同的类型, 例如 EC2 Instance, S3 Bucket, IAM Role. 搜索每种类型的资源的 API 都不一样. 而 ``Searcher`` 就是对搜索特定 AWS 资源的逻辑的一个封装. 我们有一个 Searcher Base Class, 然后让负责搜索特定 AWS 资源的 Search 继承这个 Base Class, 并且实现对应的一些方法.


Code Architecture
------------------------------------------------------------------------------
**Low level modules**

    底层模块主要是实现一些抽象的基类, 使得我们实现实体类 (就是不会再被继承的类) 的时候能更轻松.

    - :mod:`aws_resource_search.base_model`: 所有 dataclasses 类的基类.
    - :mod:`aws_resource_search.base_searcher`: 所有特定 AWS Resource 的 Searcher 类的基类.
    - :mod:`aws_resource_search.downloader`: 一些帮助我们用 boto3 来下载数据的 utility 函数.
    - :mod:`aws_resource_search.searcher_enum`: 我们已实现的 searcher (也就是 resource type) 的枚举.
    - :mod:`aws_resource_search.terminal`: terminal 对象的单例.

Middle level modules:

    中层模块主要是一些跟业务逻辑相关的实体类.

    - :mod:`aws_resource_search.documents`: 所有的可以被搜索的文档的实体类.
    - :mod:`aws_resource_search.items`: 所有在 UI 中展示的 item 的实体类.
    - :mod:`aws_resource_search.conf`: 配置管理系统.
    - :mod:`aws_resource_search.res_lib.py`: 把所有底层, 中层模块的方法都注册到这个模块中, 以便于其他模块可以直接 import 这个模块, 而不用 import 太多的模块.

Per AWS Resource Type Searcher modules:

    这一层主要是实现对应的 AWS Resource 的 Searcher 类. 以及把他们汇总到一个 ``ARS`` 单例对象中, 便于 import 和调用 search 的 API.

    - :mod:`aws_resource_search.res`
    - :mod:`aws_resource_search.ars_def`: ARS 类的基类.
    - :mod:`aws_resource_search.ars_mixin`: 用 code 来写 code, 自动生成这个模块.
    - :mod:`aws_resource_search.ars_search_patterns.py`: 把一些 ``ars_def`` 中的方法放到其他 mixin 类中去, 以便于 ``ars_def`` 中的代码更简洁.
    - :mod:`aws_resource_search.ars_init`: ARS 单例的创建.

UI modules:

    这一层主要是实现 UI.

    - :mod:`aws_resource_search.handlers`: 所有 UI 中会用到的 handler 的实现.
    - :mod:`aws_resource_search.ui_def`: UI 类的定义.
    - :mod:`aws_resource_search.ui_init`: UI 单例的创建.

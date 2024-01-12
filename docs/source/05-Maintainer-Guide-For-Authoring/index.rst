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
当你在命令行输入 ``ars`` 的时候, 就会调用 :func:`aws_resource_search.cli.main.run` 这个函数. 由于你没有输入任何 subcommand 以及参数, 所以它会调用 :meth:`aws_resource_search.cli.ArsCli.__call__` 这个方法. 这两个函数都是位于 :mod:`aws_resource_search.cli` 这个模块中的, 是负责 CLI 的接口的用的, 并不涉及具体业务逻辑. 而你看 ``__call__`` 这个方法就知道, 里面会调用 :func:`aws_resource_search.ui.main.run_ui` 这个函数. 这个函数是位于 :mod:`aws_resource_search.ui` 下的, 属于 UI 的核心逻辑.


UI Event Loop
------------------------------------------------------------------------------
UI 的入口函数 :func:`aws_resource_search.ui.main.run_ui` 里面的内容和恩简单, 就是实例化一个 :class:`aws_resource_search.ui.main.UI` 对象, 然后进入 event loop. 对于 UI 来说, 你每按下一个按键, 都会调用一个函数来处理你的输入, 然后重新渲染整个界面. 这个用于处理输入的函数就是 :func:`aws_resource_search.ui.main.handler`


UI Handler
------------------------------------------------------------------------------


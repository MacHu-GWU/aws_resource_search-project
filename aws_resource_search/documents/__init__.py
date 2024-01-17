# -*- coding: utf-8 -*-

"""
[CN] maintainer note

Resource Search 的核心是根据 searchable document. 一个 Document 代表着一个类似于字典的
数据结构, 只不过它是能被 whoosh 所索引并搜索的. 从 AWS API 上抓下来的数据要被转换成
Document, 保存在 whoosh 的 index 里面. 在搜索的时候, 我们会 match 到一些 Document,
我们将其反序列化为 Document 对象, 然后生成 UI 的 dropdown menu 所需的
:class:`aws_resource_search.items.base_item.BaseArsItem` 对象.`

这个模块定义了所有 Document 的基类以及实体类.
"""

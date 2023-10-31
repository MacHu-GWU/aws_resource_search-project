AWS Resource Search
==============================================================================


Why this Project
------------------------------------------------------------------------------
**Objectives**

这个项目是希望能提供一套类似于 Google Search 一样的搜索 API, 只需要输入文本即可对多个 AWS Account, 多个 AWS Region 上的 Resource 进行搜索.

这个项目的独特之处在于:

- 搜索性能极高, 匹配准确度极高, 并且支持模糊搜索. 这是因为该项目构建于全文搜索技术之上, 并且使用了 Ngram index. 无论是 AWS Resource 的数据集和 Query 都默认使用本地高效缓存. 使得搜索体验远超 AWS Console.
- 可以通过切换 AWS Profile 或者 Credential 非常轻松地切换所要搜索的 AWS Account 和 Region.
- 返回的数据中不仅包含有 AWS Resource 的 Data Model 中的全部字段, 还有一个 console_url 字段可以让用户点击一键跳转到 AWS Console 中查看该 Resource 的详细信息. 以及常用的 ARN 字段供用户拷贝.

**Background**

早期这个项目是我个人构建的 Alfred AWS Tool Workflow 的子模块, 用于给 UI 界面提供搜索功能. 但是后来经过评估认为, 这个模块可以单独拿出来成为一个开源项目, 更好的对其进行充分测试, 以保证底层功能的正确性以及可维护性. 并提供一套底层 API 供其他项目使用, 而不仅限于 Alfred AWS Tool Workflow 这个以 UI 界面为主的使用.



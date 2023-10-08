


- ``${aws_account_id}_${aws_region}_${service_id}_${resource_type}``
- ``(${aws_account_id}_${aws_region}_${service_id}_${resource_type}, ${query}, ${limit})``

Cache Strategy
------------------------------------------------------------------------------
本节我们来探讨一下 AWS Resource Search (ARS) 的缓存策略.

首先, 我们来回顾一个 ARS 的搜索流程. 你先要有一个 boto session, 然后指定某一种 AWS resource 对其进行搜索. 这会发起一个 boto API call, 把数据拉取下来. 注意这个 boto API call 可能会有参数. 例如你获取所有的 glue tables 的数据的时候需要指定一个 database name, 再比如你要获取某个 Lambda function 的所有 version 的时候需要指定 function name. 这些被拉取的数据会被 index. 然后你就可以通过 full text search 来搜索了, 你的搜索会有 query string, 会有 limit, 以及其他的参数. 最终 ARS 会把结果返回给用户.

由此可知, 我们在两个节点需要做缓存:

1. Data Cache: 将数据成功 index 好的时候要在缓存中将其标记为成功, 下次查询的时候就不用重新运行 boto API call 以及 index 了.
2. Query Cache: 每当 Query 结果返回的时候就要做缓存, 下次查询的时候如果 Query 相同则直接返回缓存结果.

好了, 我们来看看对于这两种缓存, 我们应该如何设计 cache key. 为了方便说明, 我们先来讨论一个作为一个唯一标识符的 key, 它可能可以包含哪些部分:

1. bsm finger print: ``${aws_account_id}_${aws_region}`` 或 ``${aws_profile}_${aws_region}``, 例如 ``123456789012_us-east-1`` 或 ``default_us-east-1``, 它是你当前所使用的 boto session 的唯一标识.
2. service and resource: ``${service_id}_${resource_type}``, 例如 ``s3_bucket``, ``ec2_instance``, 它是你目前所查询的 AWS 服务和 AWS 资源的唯一值标识
3. context: ``${bsm finger print}_${service and resource}``, 前面两个合起来就成为 ``context``.
4. ``boto argument``: 你在运行 boto API call 时所使用的参数. 当然你不需要用整个字典作为参数, 往往你只需要其中的某个属性作为参数就好了.
5. ``query arguments``: 你在运行 query 的时候所使用的参数, 包括了 query string, limit 等.

所谓缓存 key 本质上就是这些组成部分的排列组合. 然后我们来看, 我们应该选取哪些部分构成缓存 key.

1. Data Cache: ``context`` + ``boto argument``.
2. Query Cache: ``context`` + ``boto argument`` + ``query arguments`` 即可. 这里一定要加上 ``boto argument`` 是因为我们的 query 是基于 dataset 的, 而 dataset 又是由 ``boto argument`` 决定的, 如果数据变了, query 的缓存是没有意义的.

讨论完了缓存 key 的策略, 我们还需要缓存一个淘汰策略. 删除缓存的方式有两种, 一种是用 key, 还有一种是用 tag 来批量删除. key 自然不用说, 你查询的时候先检查缓存, 你删除的时候用同样的 key 删除缓存即可. 这里我们重点讨论 tag 的策略.

1. Query Cache Tag: 我们要忽略缓存的时候往往是因为上游的数据已经过期了. 而由于 query 是有参数的, 所以同一份数据的 query 缓存是不同的, 当我们因为上游数据过期清除缓存的时候, 需要将所有跟上游数据关联的缓存全部清除. 也就是说, 当我们写入 Query Cache 的时候, 我们应用 ``context`` + ``boto argument`` 来作为 tag, 而无视 query 参数的变化, 这样就能一次性的删除所有跟上游数据有关的缓存了. 注意, 我们在重新获取上游数据的时候, 自然也要更新 Data Cache
2. Data Cache Tag: 当我们完成 index, 在缓存做标记时, `应该使用 ``context`` + ``boto argument`` 来作为 tag, 因为


- 所有的 ``context`` Index

Example
------------------------------------------------------------------------------

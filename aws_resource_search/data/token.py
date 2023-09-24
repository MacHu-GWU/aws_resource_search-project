# -*- coding: utf-8 -*-

"""
Token 是一个需要被 evaluate 之后才能获得的值.
"""

import typing as T
import copy
import dataclasses
import jmespath

from .common import BaseModel


@dataclasses.dataclass
class BaseToken(BaseModel):
    pass


@dataclasses.dataclass
class StringTemplateToken(BaseToken):
    """
    这种类型的 Token 是一个字符串模板, 而模板中的变量都是从一个叫 ``data`` 的字典对象中通过
    jmespath 语法获取的.

    举例, 我们的 template 是 ``Hello {FIRSTNAME} {LASTNAME}!  Today is {DATE}.``,
    而我们的 data 如下::

        {"first_name": "John", "last_name": "Doe"}

    这个 FIRSTNAME, LASTNAME 需要从 data 中提取出来 (虽然看似不需要做任何处理, 但这里只是举例,
    用来说明这个 "提取" 的过程). 其中 params 参数如下::

        {
            "FIRSTNAME": "$first_name",
            "LASTNAME": "$last_name",
        }

    这个 params 的意思是从 data 中提取 ``$first_name`` 给 ``FIRSTNAME``, 提取 ``$last_name``
    给 ``LASTNAME``. 这里的 ``$first_name`` 是 jmespath 语法. 之后的 params 就可以作为
    字符串模板的参数, 通过 ``template.format(**params)`` 来最终生成字符串.

    除此之外, 我们还有一个 context 的概念, 这个 context 是一个字典对象, 用来提供额外的数据.
    这些数据既可以用于数据提取, 也可以用于字符串模板的参数. 例如, 这里的 context 是::

        {"DATE": "2021-01-01"}

    总结下来, ``StringTemplateToken`` 的使用方法是::

        >>> token = StringTemplateToken(
        ...     template="Hello {FIRSTNAME} {LASTNAME}! Today is {DATE}.",
        ...     params={
        ...         "FIRSTNAME": "$first_name",
        ...         "LASTNAME": "$last_name",
        ...     },
        ... )
        >>> token.evaluate(
        ...     data={"first_name": "John", "last_name": "Doe"},
        ...     context={"DATE": "2021-01-01"},
        ... )
        'Hello John Doe! Today is 2021-01-01.'
    """

    template: str = dataclasses.field()
    params: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    _type: str = "string_template"

    def evaluate(
        self,
        data: T.Dict[str, T.Any],
        context: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> str:
        data = copy.copy(data)
        params = dict()
        if context is not None:
            data.update(context)
            params.update(context)

        for k, v in self.params.items():
            if v.startswith("$"):
                expr = jmespath.compile(v[1:])
                params[k] = expr.search(data)
            else:  # pragma: no cover
                params[k] = v

        return self.template.format(**params)


token_class_mapper = {klass._type: klass for klass in BaseToken.__subclasses__()}

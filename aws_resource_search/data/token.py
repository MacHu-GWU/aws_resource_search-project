# -*- coding: utf-8 -*-

"""
Token 是一个需要被 evaluate 之后才能获得的值. 本模块实现如何定义一个 Token, 以及如何
evaluate 最终的值, 以及定义了一些常用的 Token.
"""

import typing as T
import dataclasses
import jmespath

from .common import BaseModel
from .types import T_EVAL_DATA
from ..constants import TokenTypeEnum


@dataclasses.dataclass
class BaseToken(BaseModel):
    """
    所有 Token 的基类.

    所有的 Token 必须有一些属性定义了这个 Token 是如何被 evaluate 的规则. 例如
    :class:`JmespathToken`` 就有一个 ``path`` 属性, 定义了如何从 data 中提取最终的
    value. 这些属性的定义取决于你的 Token 的 evaluation 的规则.

    所有的 Token 类必须有一个 ``def evaluate(data: T_EVAL_DATA):`` 方法. 这个方法的作用是根据
     ``data`` 和 evaluation 的规则提取储最终的 value. 这个 data 通常是一个 dict 对象,
     但也可以是 list, str, int, float, bool 等任何可以用 jmespath 处理的对象.
    """

    def evaluate(
        self,
        data: T_EVAL_DATA,
    ) -> T.Any:  # pragma: no cover
        raise NotImplementedError


@dataclasses.dataclass
class RawToken(BaseToken):
    """
    这种类型的 token 会将 value 中的值原封不动的返回.

    :param value: 所要返回的值. 可以是任何对象.
    """

    value: T.Any = dataclasses.field()

    def evaluate(self, data: T_EVAL_DATA) -> T.Any:  # pragma: no cover
        return self.value


@dataclasses.dataclass
class JmespathToken(BaseToken):
    """
    这种类型的 token 会从一个叫 ``data`` 的字典对象中通过 jmespath 语法获取最终的值.

    :param path: jmespath 的语法.
    """

    path: str = dataclasses.field()

    def evaluate(self, data: T_EVAL_DATA) -> T.Any:  # pragma: no cover
        return jmespath.search(self.path[1:], data)


@dataclasses.dataclass
class SubToken(BaseToken):
    """
    这种类型的 token 是一个字符串模板, 而模板中的变量都是从一个叫 ``data`` 的字典对象中通过
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

    总结下来, ``SubToken`` 的使用方法是::

        >>> token = SubToken(
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

    :param template: 字符串模板.
    :param params: 字符串模板所需的数据, 是一个 key value 键值对, 其中值既可以是 literal,
        也可以是一个 token.
    """

    template: str = dataclasses.field()
    params: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    def _evaluate_params(self, data: T_EVAL_DATA) -> T.Dict[str, T.Any]:
        """ """
        params = dict()
        for k, v in self.params.items():
            params[k] = evaluate_token(v, data)
        return params

    def evaluate(self, data: T_EVAL_DATA) -> str:
        """
        todo: add docstring
        """
        format_data = self._evaluate_params(data)
        return self.template.format(**format_data)


@dataclasses.dataclass
class JoinToken(BaseToken):
    sep: str = dataclasses.field()
    array: T.List[T.Any] = dataclasses.field(default_factory=list)

    def _evaluate_array(self, data: T_EVAL_DATA) -> T.List[str]:
        """ """
        array = list()
        for v in self.array:
            array.append(evaluate_token(v, data))
        return array

    def evaluate(self, data: T_EVAL_DATA) -> str:
        """
        todo: add docstring
        """
        array = self._evaluate_array(data)
        return self.sep.join(array)


token_class_mapper = {
    TokenTypeEnum.raw.value: RawToken,
    TokenTypeEnum.jmespath.value: JmespathToken,
    TokenTypeEnum.sub.value: SubToken,
    TokenTypeEnum.join.value: JoinToken,
}


def evaluate_token(
    token: T.Any,
    data: T_EVAL_DATA,
) -> T.Any:
    """
    自动判断 token 是什么类型, 应该用什么策略来 evaluate.

    **如果 Token 是一个字符串**, 那么有两种情况:

    1. 字符串以 ``$`` 开头, 表示这是一个 jmespath 语法, 那么自动将其作为
        ``JmespathToken(path=token)`` 来 evaluate 数据.
    2. 字符串中包含 Python 中的 string template 语法, 类似 ``{key}`` 这种, 则表示这是
        一个 string template, 而 data 就作为参数传给这个 string template, 使用
        ``token.format(**data)`` 来 evaluate 数据. 值得注意的是, 如果这个 token 中
        不包含 string template 语法, ``token.format(**data)`` 也不会失败, 只不过没有
        任何效果, 只是将这个 string 原样返回而已.

    **如果 Token 是一个字典**, 那么这个 token 就是一个用于创建 Token 对象的数据. 这个字典必定包含
    ``type`` 和 ``kwargs`` 字段.

    - ``type`` 字段代表这个 token 的类型, 它的值必须是
    :class:`~aws_resource_search.constants.TokenTypeEnum` 中所定义的. 每一个 Type
        都对应着此模块下定义的一个 Token 类. 例如 :class:`SubToken``, :class:`JoinToken``
    - ``kwargs`` 字典代表了创建 Token 类所用到的参数. 例如 :class:`SubToken`` 的参数是
        ``{"template": "my_string_template", "params": {"key": "value"}}``.

    例如下面这个就是一个 :class:`SubToken` 的例子::

        {
            "type": "sub",
            "kwargs": {
                "template": "arn:aws:s3:::{bucket}",
                "params": {
                    "bucket": "$Name"
                }
            }
        }

    **如果 Token 不是字符串也不是字典**, 那么就视其为 literal, 直接返回. 这里注意的是如果
    你的 literal 恰巧也是一个字典, 你需要用 ``RawToken`` 的语法显式的指定它是一个 Raw,
    例如 ``{"type": "raw", "kwargs": {"value": my_dictionary_here}}``. 不然它会被
    解析为一个 Token 对象.
    """
    if isinstance(token, str):
        if token.startswith("$"):
            return JmespathToken(path=token).evaluate(data)
        else:  # literal
            return token
    elif isinstance(token, dict):
        if "type" in token:
            token_type = token["type"]
            token_class = token_class_mapper[token_type]
            return token_class(**token["kwargs"]).evaluate(data)
        else:  # literal
            return token
    else:  # literal
        return token

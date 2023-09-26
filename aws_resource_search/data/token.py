# -*- coding: utf-8 -*-

"""
Token 是一个需要被 evaluate 之后才能获得的值.
"""

import typing as T
import copy
import dataclasses
import jmespath

from .common import BaseModel
from ..constants import TokenTypeEnum


@dataclasses.dataclass
class BaseToken(BaseModel):
    """
    所有 Token 的基类.

    所有的 Token 类必须有一个 ``def evaluate(data: dict, context: T.Optional[dict]):``
    方法. 这个方法的作用是根据 ``data`` 和 ``context`` 来计算出这个 Token 的值.
    """

    def evaluate(
        self,
        data: T.Dict[str, T.Any],
        context: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> T.Any:  # pragma: no cover
        raise NotImplementedError


@dataclasses.dataclass
class RawToken(BaseToken):
    """
    这种类型的 token 会将 value 中的值原封不动的返回.

    :param value: 所要返回的值. 可以是任何对象.
    """

    value: T.Any = dataclasses.field()

    def evaluate(
        self,
        data: T.Dict[str, T.Any],
        context: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> T.Any:  # pragma: no cover
        return self.value


@dataclasses.dataclass
class JmespathToken(BaseToken):
    """
    这种类型的 token 会从一个叫 ``data`` 的字典对象中通过 jmespath 语法获取最终的值.

    :param path: jmespath 的语法.
    """

    path: str = dataclasses.field()

    def evaluate(
        self,
        data: T.Dict[str, T.Any],
        context: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> T.Any:  # pragma: no cover
        if context is None:
            context = data
        else:
            context = copy.copy(context)
            context.update(data)
        return jmespath.search(self.path[1:], context)


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

    def _evaluate_params(
        self,
        data: T.Dict[str, T.Any],
        context: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> T.Dict[str, T.Any]:
        """ """
        params = dict()
        for k, v in self.params.items():
            params[k] = evaluate_token(v, data, context)
        return params

    def evaluate(
        self,
        data: T.Dict[str, T.Any],
        context: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> str:
        """
        todo: add docstring
        """
        if context is None:  # pragma: no cover
            context = dict()
        else:  # pragma: no cover
            context = copy.copy(context)
        evaluate_data = dict()
        evaluate_data.update(data)
        evaluate_data.update(context)
        format_data = self._evaluate_params(evaluate_data, context)
        format_data.update(context)
        return self.template.format(**format_data)


@dataclasses.dataclass
class JoinToken(BaseToken):
    sep: str = dataclasses.field()
    array: T.List[T.Any] = dataclasses.field(default_factory=list)

    def _evaluate_array(
        self,
        data: T.Dict[str, T.Any],
        context: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> T.List[str]:
        """ """
        array = list()
        for v in self.array:
            array.append(evaluate_token(v, data, context))
        return array

    def evaluate(
        self,
        data: T.Dict[str, T.Any],
        context: T.Optional[T.Dict[str, T.Any]] = None,
    ) -> str:
        """
        todo: add docstring
        """
        if context is None:  # pragma: no cover
            context = dict()
        else:  # pragma: no cover
            context = copy.copy(context)
        evaluate_data = dict()
        evaluate_data.update(data)
        evaluate_data.update(context)
        array = self._evaluate_array(evaluate_data, context)
        return self.sep.join(array)


token_class_mapper = {
    TokenTypeEnum.raw.value: RawToken,
    TokenTypeEnum.jmespath.value: JmespathToken,
    TokenTypeEnum.sub.value: SubToken,
    TokenTypeEnum.join.value: JoinToken,
}


def evaluate_token(
    token: T.Any,
    data: T.Dict[str, T.Any],
    context: T.Optional[T.Dict[str, T.Any]] = None,
) -> T.Any:
    """
    自动判断 token 是什么类型, 应该用什么策略来 evaluate.
    """
    if isinstance(token, str):
        if token.startswith("$"):
            return JmespathToken(path=token).evaluate(data, context)
        else:
            return token
    elif isinstance(token, dict):
        token_type = token["type"]
        token_class = token_class_mapper[token_type]
        return token_class(**token["kwargs"]).evaluate(data, context)
    else:
        return token

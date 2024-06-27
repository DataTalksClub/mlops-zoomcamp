from __future__ import annotations

import random
from abc import ABC, abstractmethod
from collections import deque
from typing import Any

from polyfactory.utils.predicates import is_safe_subclass


class CollectionExtender(ABC):
    __types__: tuple[type, ...]

    @staticmethod
    @abstractmethod
    def _extend_type_args(type_args: tuple[Any, ...], number_of_args: int) -> tuple[Any, ...]:
        raise NotImplementedError

    @classmethod
    def _subclass_for_type(cls, annotation_alias: Any) -> type[CollectionExtender]:
        return next(
            (
                subclass
                for subclass in cls.__subclasses__()
                if any(is_safe_subclass(annotation_alias, t) for t in subclass.__types__)
            ),
            FallbackExtender,
        )

    @classmethod
    def extend_type_args(
        cls,
        annotation_alias: Any,
        type_args: tuple[Any, ...],
        number_of_args: int,
    ) -> tuple[Any, ...]:
        return cls._subclass_for_type(annotation_alias)._extend_type_args(type_args, number_of_args)


class TupleExtender(CollectionExtender):
    __types__ = (tuple,)

    @staticmethod
    def _extend_type_args(type_args: tuple[Any, ...], number_of_args: int) -> tuple[Any, ...]:
        if not type_args:
            return type_args
        if type_args[-1] is not ...:
            return type_args
        type_to_extend = type_args[-2]
        return type_args[:-2] + (type_to_extend,) * number_of_args


class ListLikeExtender(CollectionExtender):
    __types__ = (list, deque)

    @staticmethod
    def _extend_type_args(type_args: tuple[Any, ...], number_of_args: int) -> tuple[Any, ...]:
        if not type_args:
            return type_args
        return tuple(random.choice(type_args) for _ in range(number_of_args))


class SetExtender(CollectionExtender):
    __types__ = (set, frozenset)

    @staticmethod
    def _extend_type_args(type_args: tuple[Any, ...], number_of_args: int) -> tuple[Any, ...]:
        if not type_args:
            return type_args
        return tuple(random.choice(type_args) for _ in range(number_of_args))


class DictExtender(CollectionExtender):
    __types__ = (dict,)

    @staticmethod
    def _extend_type_args(type_args: tuple[Any, ...], number_of_args: int) -> tuple[Any, ...]:
        return type_args * number_of_args


class FallbackExtender(CollectionExtender):
    __types__ = ()

    @staticmethod
    def _extend_type_args(
        type_args: tuple[Any, ...],
        number_of_args: int,  # noqa: ARG004
    ) -> tuple[Any, ...]:  # - investigate @guacs
        return type_args

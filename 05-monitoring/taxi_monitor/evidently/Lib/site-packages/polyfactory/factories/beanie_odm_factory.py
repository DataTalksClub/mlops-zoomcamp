from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from typing_extensions import get_args

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.persistence import AsyncPersistenceProtocol
from polyfactory.utils.predicates import is_safe_subclass

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

    from polyfactory.factories.base import BuildContext
    from polyfactory.field_meta import FieldMeta

try:
    from beanie import Document
except ImportError as e:
    msg = "beanie is not installed"
    raise MissingDependencyException(msg) from e

T = TypeVar("T", bound=Document)


class BeaniePersistenceHandler(Generic[T], AsyncPersistenceProtocol[T]):
    """Persistence Handler using beanie logic"""

    async def save(self, data: T) -> T:
        """Persist a single instance in mongoDB."""
        return await data.insert()  # pyright: ignore[reportGeneralTypeIssues]

    async def save_many(self, data: list[T]) -> list[T]:
        """Persist multiple instances in mongoDB.

        .. note:: we cannot use the ``.insert_many`` method from Beanie here because it doesn't
            return the created instances
        """
        return [await doc.insert() for doc in data]  # pyright: ignore[reportGeneralTypeIssues]


class BeanieDocumentFactory(Generic[T], ModelFactory[T]):
    """Base factory for Beanie Documents"""

    __async_persistence__ = BeaniePersistenceHandler
    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[type[T]]":
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        return is_safe_subclass(value, Document)

    @classmethod
    def get_field_value(
        cls,
        field_meta: "FieldMeta",
        field_build_parameters: Any | None = None,
        build_context: BuildContext | None = None,
    ) -> Any:
        """Return a field value on the subclass if existing, otherwise returns a mock value.

        :param field_meta: FieldMeta instance.
        :param field_build_parameters: Any build parameters passed to the factory as kwarg values.

        :returns: An arbitrary value.

        """
        if hasattr(field_meta.annotation, "__name__"):
            if "Indexed " in field_meta.annotation.__name__:
                base_type = field_meta.annotation.__bases__[0]
                field_meta.annotation = base_type

            if "Link" in field_meta.annotation.__name__:
                link_class = get_args(field_meta.annotation)[0]
                field_meta.annotation = link_class
                field_meta.annotation = link_class

        return super().get_field_value(
            field_meta=field_meta,
            field_build_parameters=field_build_parameters,
            build_context=build_context,
        )

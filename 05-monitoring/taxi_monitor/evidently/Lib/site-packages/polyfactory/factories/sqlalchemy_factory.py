from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Generic, List, TypeVar, Union

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import FieldMeta
from polyfactory.persistence import AsyncPersistenceProtocol, SyncPersistenceProtocol

try:
    from sqlalchemy import Column, inspect, types
    from sqlalchemy.dialects import mssql, mysql, postgresql, sqlite
    from sqlalchemy.exc import NoInspectionAvailable
    from sqlalchemy.orm import InstanceState, Mapper
except ImportError as e:
    msg = "sqlalchemy is not installed"
    raise MissingDependencyException(msg) from e

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session
    from typing_extensions import TypeGuard


T = TypeVar("T")


class SQLASyncPersistence(SyncPersistenceProtocol[T]):
    def __init__(self, session: Session) -> None:
        """Sync persistence handler for SQLAFactory."""
        self.session = session

    def save(self, data: T) -> T:
        self.session.add(data)
        self.session.commit()
        return data

    def save_many(self, data: list[T]) -> list[T]:
        self.session.add_all(data)
        self.session.commit()
        return data


class SQLAASyncPersistence(AsyncPersistenceProtocol[T]):
    def __init__(self, session: AsyncSession) -> None:
        """Async persistence handler for SQLAFactory."""
        self.session = session

    async def save(self, data: T) -> T:
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def save_many(self, data: list[T]) -> list[T]:
        self.session.add_all(data)
        await self.session.commit()
        for batch_item in data:
            await self.session.refresh(batch_item)
        return data


class SQLAlchemyFactory(Generic[T], BaseFactory[T]):
    """Base factory for SQLAlchemy models."""

    __is_base_factory__ = True

    __set_primary_key__: ClassVar[bool] = True
    """Configuration to consider primary key columns as a field or not."""
    __set_foreign_keys__: ClassVar[bool] = True
    """Configuration to consider columns with foreign keys as a field or not."""
    __set_relationships__: ClassVar[bool] = False
    """Configuration to consider relationships property as a model field or not."""

    __session__: ClassVar[Session | Callable[[], Session] | None] = None
    __async_session__: ClassVar[AsyncSession | Callable[[], AsyncSession] | None] = None

    __config_keys__ = (
        *BaseFactory.__config_keys__,
        "__set_primary_key__",
        "__set_foreign_keys__",
        "__set_relationships__",
    )

    @classmethod
    def get_sqlalchemy_types(cls) -> dict[Any, Callable[[], Any]]:
        """Get mapping of types where column type.
        for sqlalchemy dialect `JSON` type, accepted only basic types in pydict in case sqlalchemy process `JSON` raise serialize error.
        """
        return {
            types.TupleType: cls.__faker__.pytuple,
            mssql.JSON: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            mysql.YEAR: lambda: cls.__random__.randint(1901, 2155),
            mysql.JSON: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            postgresql.CIDR: lambda: cls.__faker__.ipv4(network=True),
            postgresql.DATERANGE: lambda: (cls.__faker__.past_date(), date.today()),  # noqa: DTZ011
            postgresql.INET: lambda: cls.__faker__.ipv4(network=False),
            postgresql.INT4RANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.INT8RANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.MACADDR: lambda: cls.__faker__.hexify(text="^^:^^:^^:^^:^^:^^", upper=True),
            postgresql.NUMRANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.TSRANGE: lambda: (cls.__faker__.past_datetime(), datetime.now()),  # noqa: DTZ005
            postgresql.TSTZRANGE: lambda: (cls.__faker__.past_datetime(), datetime.now()),  # noqa: DTZ005
            postgresql.HSTORE: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            postgresql.JSON: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            postgresql.JSONB: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            sqlite.JSON: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            types.JSON: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
        }

    @classmethod
    def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
        providers_map = super().get_provider_map()
        providers_map.update(cls.get_sqlalchemy_types())
        return providers_map

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        try:
            inspected = inspect(value)
        except NoInspectionAvailable:
            return False
        return isinstance(inspected, (Mapper, InstanceState))

    @classmethod
    def should_column_be_set(cls, column: Any) -> bool:
        if not isinstance(column, Column):
            return False

        if not cls.__set_primary_key__ and column.primary_key:
            return False

        return bool(cls.__set_foreign_keys__ or not column.foreign_keys)

    @classmethod
    def get_type_from_column(cls, column: Column) -> type:
        column_type = type(column.type)
        sqla_types = cls.get_sqlalchemy_types()
        if column_type in sqla_types:
            annotation = column_type
        elif issubclass(column_type, postgresql.ARRAY):
            if type(column.type.item_type) in sqla_types:  # type: ignore[attr-defined]
                annotation = List[type(column.type.item_type)]  # type: ignore[attr-defined,misc]
            else:
                annotation = List[column.type.item_type.python_type]  # type: ignore[assignment,name-defined]
        elif issubclass(column_type, types.ARRAY):
            annotation = List[column.type.item_type.python_type]  # type: ignore[assignment,name-defined]
        else:
            try:
                annotation = column.type.python_type
            except NotImplementedError:
                annotation = column.type.impl.python_type  # type: ignore[attr-defined]

        if column.nullable:
            annotation = Union[annotation, None]  # type: ignore[assignment]
        return annotation

    @classmethod
    def get_model_fields(cls) -> list[FieldMeta]:
        fields_meta: list[FieldMeta] = []

        table: Mapper = inspect(cls.__model__)  # type: ignore[assignment]
        fields_meta.extend(
            FieldMeta.from_type(
                annotation=cls.get_type_from_column(column),
                name=name,
                random=cls.__random__,
            )
            for name, column in table.columns.items()
            if cls.should_column_be_set(column)
        )
        if cls.__set_relationships__:
            for name, relationship in table.relationships.items():
                class_ = relationship.entity.class_
                annotation = class_ if not relationship.uselist else List[class_]  # type: ignore[valid-type]
                fields_meta.append(
                    FieldMeta.from_type(
                        name=name,
                        annotation=annotation,
                        random=cls.__random__,
                    ),
                )

        return fields_meta

    @classmethod
    def _get_sync_persistence(cls) -> SyncPersistenceProtocol[T]:
        if cls.__session__ is not None:
            return (
                SQLASyncPersistence(cls.__session__())
                if callable(cls.__session__)
                else SQLASyncPersistence(cls.__session__)
            )
        return super()._get_sync_persistence()

    @classmethod
    def _get_async_persistence(cls) -> AsyncPersistenceProtocol[T]:
        if cls.__async_session__ is not None:
            return (
                SQLAASyncPersistence(cls.__async_session__())
                if callable(cls.__async_session__)
                else SQLAASyncPersistence(cls.__async_session__)
            )
        return super()._get_async_persistence()

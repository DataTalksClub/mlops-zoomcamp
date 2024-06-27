"""A repository implementation for tests.

Uses a `dict` for storage.
"""

from __future__ import annotations

from datetime import datetime, timezone, tzinfo
from typing import TYPE_CHECKING, Generic, Protocol, TypeVar
from uuid import uuid4

from litestar.repository import AbstractAsyncRepository, AbstractSyncRepository, FilterTypes
from litestar.repository.exceptions import ConflictError, RepositoryError

if TYPE_CHECKING:
    from collections.abc import Callable, Hashable, Iterable, MutableMapping
    from typing import Any

__all__ = ("GenericAsyncMockRepository", "GenericSyncMockRepository")


class HasID(Protocol):
    id: Any


ModelT = TypeVar("ModelT", bound="HasID")
AsyncMockRepoT = TypeVar("AsyncMockRepoT", bound="GenericAsyncMockRepository")
SyncMockRepoT = TypeVar("SyncMockRepoT", bound="GenericSyncMockRepository")


class GenericAsyncMockRepository(AbstractAsyncRepository[ModelT], Generic[ModelT]):
    """A repository implementation for tests.

    Uses a :class:`dict` for storage.
    """

    collection: MutableMapping[Hashable, ModelT]
    model_type: type[ModelT]
    match_fields: list[str] | str | None = None

    _model_has_created_at: bool
    _model_has_updated_at: bool

    def __init__(
        self, id_factory: Callable[[], Any] = uuid4, tz: tzinfo = timezone.utc, allow_ids_on_add: bool = False, **_: Any
    ) -> None:
        super().__init__()
        self._id_factory = id_factory
        self.tz = tz
        self.allow_ids_on_add = allow_ids_on_add

    @classmethod
    def __class_getitem__(cls: type[AsyncMockRepoT], item: type[ModelT]) -> type[AsyncMockRepoT]:
        """Add collection to ``_collections`` for the type.

        Args:
            item: The type that the class has been parametrized with.
        """
        return type(  # pyright:ignore
            f"{cls.__name__}[{item.__name__}]",
            (cls,),
            {
                "collection": {},
                "model_type": item,
                "_model_has_created_at": hasattr(item, "created_at"),
                "_model_has_updated_at": hasattr(item, "updated_at"),
            },
        )

    def _find_or_raise_not_found(self, item_id: Any) -> ModelT:
        return self.check_not_found(self.collection.get(item_id))

    def _find_or_none(self, item_id: Any) -> ModelT | None:
        return self.collection.get(item_id)

    def _now(self) -> datetime:
        return datetime.now(tz=self.tz).replace(tzinfo=None)

    def _update_audit_attributes(self, data: ModelT, now: datetime | None = None, do_created: bool = False) -> ModelT:
        now = now or self._now()
        if self._model_has_updated_at:
            data.updated_at = now  # type:ignore[attr-defined]
            if do_created:
                data.created_at = now  # type:ignore[attr-defined]
        return data

    async def add(self, data: ModelT) -> ModelT:
        """Add ``data`` to the collection.

        Args:
            data: Instance to be added to the collection.

        Returns:
            The added instance.
        """
        if self.allow_ids_on_add is False and self.get_id_attribute_value(data) is not None:
            raise ConflictError("`add()` received identified item.")
        self._update_audit_attributes(data, do_created=True)
        if self.allow_ids_on_add is False:
            id_ = self._id_factory()
            self.set_id_attribute_value(id_, data)
        self.collection[data.id] = data
        return data

    async def add_many(self, data: Iterable[ModelT]) -> list[ModelT]:
        """Add multiple ``data`` to the collection.

        Args:
            data: Instance to be added to the collection.

        Returns:
            The added instance.
        """
        now = self._now()
        for data_row in data:
            if self.allow_ids_on_add is False and self.get_id_attribute_value(data_row) is not None:
                raise ConflictError("`add()` received identified item.")

            self._update_audit_attributes(data_row, do_created=True, now=now)
            if self.allow_ids_on_add is False:
                id_ = self._id_factory()
                self.set_id_attribute_value(id_, data_row)
                self.collection[data_row.id] = data_row
        return list(data)

    async def delete(self, item_id: Any) -> ModelT:
        """Delete instance identified by ``item_id``.

        Args:
            item_id: Identifier of instance to be deleted.

        Returns:
            The deleted instance.

        Raises:
            NotFoundError: If no instance found identified by ``item_id``.
        """
        try:
            return self._find_or_raise_not_found(item_id)
        finally:
            del self.collection[item_id]

    async def delete_many(self, item_ids: list[Any]) -> list[ModelT]:
        """Delete instances identified by list of identifiers ``item_ids``.

        Args:
            item_ids: list of identifiers of instances to be deleted.

        Returns:
            The deleted instances.

        """
        instances: list[ModelT] = []
        for item_id in item_ids:
            obj = await self.get_one_or_none(**{self.id_attribute: item_id})
            if obj:
                obj = await self.delete(obj.id)
                instances.append(obj)
        return instances

    async def exists(self, *filters: FilterTypes, **kwargs: Any) -> bool:
        """Return true if the object specified by ``kwargs`` exists.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Identifier of the instance to be retrieved.

        Returns:
            True if the instance was found.  False if not found..

        """
        existing = await self.count(*filters, **kwargs)
        return bool(existing)

    async def get(self, item_id: Any, **kwargs: Any) -> ModelT:
        """Get instance identified by ``item_id``.

        Args:
            item_id: Identifier of the instance to be retrieved.
            **kwargs: additional arguments

        Returns:
            The retrieved instance.

        Raises:
            NotFoundError: If no instance found identified by ``item_id``.
        """
        return self._find_or_raise_not_found(item_id)

    async def get_or_create(self, match_fields: list[str] | str | None = None, **kwargs: Any) -> tuple[ModelT, bool]:
        """Get instance identified by ``kwargs`` or create if it doesn't exist.

        Args:
            match_fields: a list of keys to use to match the existing model.  When empty, all fields are matched.
            **kwargs: Identifier of the instance to be retrieved.

        Returns:
            a tuple that includes the instance and whether it needed to be created.

        """
        match_fields = match_fields or self.match_fields
        if isinstance(match_fields, str):
            match_fields = [match_fields]
        if match_fields:
            match_filter = {
                field_name: field_value
                for field_name in match_fields
                if (field_value := kwargs.get(field_name)) is not None
            }
        else:
            match_filter = kwargs
        existing = await self.get_one_or_none(**match_filter)
        if existing:
            for field_name, new_field_value in kwargs.items():
                field = getattr(existing, field_name, None)
                if field and field != new_field_value:
                    setattr(existing, field_name, new_field_value)

            return existing, False
        return await self.add(self.model_type(**kwargs)), True  # pyright: ignore[reportGeneralTypeIssues]

    async def get_one(self, **kwargs: Any) -> ModelT:
        """Get instance identified by query filters.

        Args:
            **kwargs: Instance attribute value filters.

        Returns:
            The retrieved instance or None

        Raises:
            NotFoundError: If no instance found identified by ``kwargs``.
        """
        data = await self.list(**kwargs)
        return self.check_not_found(data[0] if data else None)

    async def get_one_or_none(self, **kwargs: Any) -> ModelT | None:
        """Get instance identified by query filters or None if not found.

        Args:
            **kwargs: Instance attribute value filters.

        Returns:
            The retrieved instance or None
        """
        data = await self.list(**kwargs)
        return data[0] if data else None

    async def count(self, *filters: FilterTypes, **kwargs: Any) -> int:
        """Count of rows returned by query.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Instance attribute value filters.

        Returns:
            Count of instances in collection, ignoring pagination.
        """
        return len(await self.list(*filters, **kwargs))

    async def update(self, data: ModelT) -> ModelT:
        """Update instance with the attribute values present on ``data``.

        Args:
            data: An instance that should have a value for :attr:`id_attribute <AsyncGenericMockRepository.id_attribute>` that exists in the
                collection.

        Returns:
            The updated instance.

        Raises:
            NotFoundError: If no instance found with same identifier as ``data``.
        """
        item = self._find_or_raise_not_found(self.get_id_attribute_value(data))
        self._update_audit_attributes(data, do_created=False)
        for key, val in model_items(data):
            setattr(item, key, val)
        return item

    async def update_many(self, data: list[ModelT]) -> list[ModelT]:
        """Update instances with the attribute values present on ``data``.

        Args:
            data: A list of instances that should have a value for :attr:`id_attribute <AsyncGenericMockRepository.id_attribute>`
                that exists in the collection.

        Returns:
            The updated instances.

        Raises:
            NotFoundError: If no instance found with same identifier as ``data``.
        """
        items = [self._find_or_raise_not_found(self.get_id_attribute_value(row)) for row in data]
        now = self._now()
        for item in items:
            self._update_audit_attributes(item, do_created=False, now=now)
            for key, val in model_items(item):
                setattr(item, key, val)
        return items

    async def upsert(self, data: ModelT) -> ModelT:
        """Update or create instance.

        Updates instance with the attribute values present on ``data``, or creates a new instance if
        one doesn't exist.

        Args:
            data: Instance to update existing, or be created. Identifier used to determine if an
                existing instance exists is the value of an attribute on `data` named as value of
                :attr:`id_attribute <AsyncGenericMockRepository.id_attribute>`.

        Returns:
            The updated or created instance.

        Raises:
            NotFoundError: If no instance found with same identifier as ``data``.
        """
        item_id = self.get_id_attribute_value(data)
        if item_id in self.collection:
            return await self.update(data)
        return await self.add(data)

    async def upsert_many(self, data: list[ModelT]) -> list[ModelT]:
        """Update or create multiple instance.

        Update instance with the attribute values present on ``data``, or create a new instance if
        one doesn't exist.

        Args:
            data: List of instances to update existing, or be created. Identifier used to determine if an
                existing instance exists is the value of an attribute on `data` named as value of
                :attr:`id_attribute <AsyncGenericMockRepository.id_attribute>`.

        Returns:
            The updated or created instances.
        """
        data_to_update = [row for row in data if self._find_or_none(self.get_id_attribute_value(row)) is not None]
        data_to_add = [row for row in data if self._find_or_none(self.get_id_attribute_value(row)) is None]

        updated_items = await self.update_many(data_to_update)
        added_items = await self.add_many(data_to_add)
        return updated_items + added_items

    async def list_and_count(
        self,
        *filters: FilterTypes,
        **kwargs: Any,
    ) -> tuple[list[ModelT], int]:
        """Get a list of instances, optionally filtered with a total row count.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Instance attribute value filters.

        Returns:
            List of instances, and count of records returned by query, ignoring pagination.
        """
        return await self.list(*filters, **kwargs), await self.count(*filters, **kwargs)

    async def list(self, *filters: FilterTypes, **kwargs: Any) -> list[ModelT]:
        """Get a list of instances, optionally filtered.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Instance attribute value filters.

        Returns:
            The list of instances, after filtering applied.
        """
        return list(self.filter_collection_by_kwargs(self.collection, **kwargs).values())

    def filter_collection_by_kwargs(  # type:ignore[override]
        self, collection: MutableMapping[Hashable, ModelT], /, **kwargs: Any
    ) -> MutableMapping[Hashable, ModelT]:
        """Filter the collection by kwargs.

        Args:
            collection: set of objects to filter
            **kwargs: key/value pairs such that objects remaining in the collection after filtering
                have the property that their attribute named ``key`` has value equal to ``value``.
        """
        new_collection: dict[Hashable, ModelT] = {}
        for item in self.collection.values():
            try:
                if all(getattr(item, name) == value for name, value in kwargs.items()):
                    new_collection[item.id] = item
            except AttributeError as orig:
                raise RepositoryError from orig
        return new_collection

    @classmethod
    def seed_collection(cls, instances: Iterable[ModelT]) -> None:
        """Seed the collection for repository type.

        Args:
            instances: the instances to be added to the collection.
        """
        for instance in instances:
            cls.collection[cls.get_id_attribute_value(instance)] = instance

    @classmethod
    def clear_collection(cls) -> None:
        """Empty the collection for repository type."""
        cls.collection = {}


class GenericSyncMockRepository(AbstractSyncRepository[ModelT], Generic[ModelT]):
    """A repository implementation for tests.

    Uses a :class:`dict` for storage.
    """

    collection: MutableMapping[Hashable, ModelT]
    model_type: type[ModelT]
    match_fields: list[str] | str | None = None

    _model_has_created_at: bool
    _model_has_updated_at: bool

    def __init__(
        self,
        id_factory: Callable[[], Any] = uuid4,
        tz: tzinfo = timezone.utc,
        allow_ids_on_add: bool = False,
        **_: Any,
    ) -> None:
        super().__init__()
        self._id_factory = id_factory
        self.tz = tz
        self.allow_ids_on_add = allow_ids_on_add

    @classmethod
    def __class_getitem__(cls: type[SyncMockRepoT], item: type[ModelT]) -> type[SyncMockRepoT]:
        """Add collection to ``_collections`` for the type.

        Args:
            item: The type that the class has been parametrized with.
        """
        return type(  # pyright:ignore
            f"{cls.__name__}[{item.__name__}]",
            (cls,),
            {
                "collection": {},
                "model_type": item,
                "_model_has_created_at": hasattr(item, "created_at"),
                "_model_has_updated_at": hasattr(item, "updated_at"),
            },
        )

    def _find_or_raise_not_found(self, item_id: Any) -> ModelT:
        return self.check_not_found(self.collection.get(item_id))

    def _find_or_none(self, item_id: Any) -> ModelT | None:
        return self.collection.get(item_id)

    def _now(self) -> datetime:
        return datetime.now(tz=self.tz).replace(tzinfo=None)

    def _update_audit_attributes(self, data: ModelT, now: datetime | None = None, do_created: bool = False) -> ModelT:
        now = now or self._now()
        if self._model_has_updated_at:
            data.updated_at = now  # type:ignore[attr-defined]
            if do_created:
                data.created_at = now  # type:ignore[attr-defined]
        return data

    def add(self, data: ModelT) -> ModelT:
        """Add ``data`` to the collection.

        Args:
            data: Instance to be added to the collection.

        Returns:
            The added instance.
        """
        if self.allow_ids_on_add is False and self.get_id_attribute_value(data) is not None:
            raise ConflictError("`add()` received identified item.")
        self._update_audit_attributes(data, do_created=True)
        if self.allow_ids_on_add is False:
            id_ = self._id_factory()
            self.set_id_attribute_value(id_, data)
        self.collection[data.id] = data
        return data

    def add_many(self, data: Iterable[ModelT]) -> list[ModelT]:
        """Add multiple ``data`` to the collection.

        Args:
            data: Instance to be added to the collection.

        Returns:
            The added instance.
        """
        now = self._now()
        for data_row in data:
            if self.allow_ids_on_add is False and self.get_id_attribute_value(data_row) is not None:
                raise ConflictError("`add()` received identified item.")

            self._update_audit_attributes(data_row, do_created=True, now=now)
            if self.allow_ids_on_add is False:
                id_ = self._id_factory()
                self.set_id_attribute_value(id_, data_row)
                self.collection[data_row.id] = data_row
        return list(data)

    def delete(self, item_id: Any) -> ModelT:
        """Delete instance identified by ``item_id``.

        Args:
            item_id: Identifier of instance to be deleted.

        Returns:
            The deleted instance.

        Raises:
            NotFoundError: If no instance found identified by ``item_id``.
        """
        try:
            return self._find_or_raise_not_found(item_id)
        finally:
            del self.collection[item_id]

    def delete_many(self, item_ids: list[Any]) -> list[ModelT]:
        """Delete instances identified by list of identifiers ``item_ids``.

        Args:
            item_ids: list of identifiers of instances to be deleted.

        Returns:
            The deleted instances.

        """
        instances: list[ModelT] = []
        for item_id in item_ids:
            if obj := self.get_one_or_none(**{self.id_attribute: item_id}):
                obj = self.delete(obj.id)
                instances.append(obj)
        return instances

    def exists(self, *filters: FilterTypes, **kwargs: Any) -> bool:
        """Return true if the object specified by ``kwargs`` exists.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Identifier of the instance to be retrieved.

        Returns:
            True if the instance was found.  False if not found..

        """
        existing = self.count(*filters, **kwargs)
        return bool(existing)

    def get(self, item_id: Any, **kwargs: Any) -> ModelT:
        """Get instance identified by ``item_id``.

        Args:
            item_id: Identifier of the instance to be retrieved.
            **kwargs: additional arguments

        Returns:
            The retrieved instance.

        Raises:
            NotFoundError: If no instance found identified by ``item_id``.
        """
        return self._find_or_raise_not_found(item_id)

    def get_or_create(self, match_fields: list[str] | str | None = None, **kwargs: Any) -> tuple[ModelT, bool]:
        """Get instance identified by ``kwargs`` or create if it doesn't exist.

        Args:
            match_fields: a list of keys to use to match the existing model.  When empty, all fields are matched.
            **kwargs: Identifier of the instance to be retrieved.

        Returns:
            a tuple that includes the instance and whether it needed to be created.

        """
        match_fields = match_fields or self.match_fields
        if isinstance(match_fields, str):
            match_fields = [match_fields]
        if match_fields:
            match_filter = {
                field_name: field_value
                for field_name in match_fields
                if (field_value := kwargs.get(field_name)) is not None
            }
        else:
            match_filter = kwargs
        if existing := self.get_one_or_none(**match_filter):
            for field_name, new_field_value in kwargs.items():
                field = getattr(existing, field_name, None)
                if field and field != new_field_value:
                    setattr(existing, field_name, new_field_value)

            return existing, False
        return self.add(self.model_type(**kwargs)), True  # pyright: ignore[reportGeneralTypeIssues]

    def get_one(self, **kwargs: Any) -> ModelT:
        """Get instance identified by query filters.

        Args:
            **kwargs: Instance attribute value filters.

        Returns:
            The retrieved instance or None

        Raises:
            NotFoundError: If no instance found identified by ``kwargs``.
        """
        data = self.list(**kwargs)
        return self.check_not_found(data[0] if data else None)

    def get_one_or_none(self, **kwargs: Any) -> ModelT | None:
        """Get instance identified by query filters or None if not found.

        Args:
            **kwargs: Instance attribute value filters.

        Returns:
            The retrieved instance or None
        """
        data = self.list(**kwargs)
        return data[0] if data else None

    def count(self, *filters: FilterTypes, **kwargs: Any) -> int:
        """Count of rows returned by query.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Instance attribute value filters.

        Returns:
            Count of instances in collection, ignoring pagination.
        """
        return len(self.list(*filters, **kwargs))

    def update(self, data: ModelT) -> ModelT:
        """Update instance with the attribute values present on ``data``.

        Args:
            data: An instance that should have a value for :attr:`id_attribute <AsyncGenericMockRepository.id_attribute>` that exists in the
                collection.

        Returns:
            The updated instance.

        Raises:
            NotFoundError: If no instance found with same identifier as ``data``.
        """
        item = self._find_or_raise_not_found(self.get_id_attribute_value(data))
        self._update_audit_attributes(data, do_created=False)
        for key, val in model_items(data):
            setattr(item, key, val)
        return item

    def update_many(self, data: list[ModelT]) -> list[ModelT]:
        """Update instances with the attribute values present on ``data``.

        Args:
            data: A list of instances that should have a value for :attr:`id_attribute <AsyncGenericMockRepository.id_attribute>`
                that exists in the collection.

        Returns:
            The updated instances.

        Raises:
            NotFoundError: If no instance found with same identifier as ``data``.
        """
        items = [self._find_or_raise_not_found(self.get_id_attribute_value(row)) for row in data]
        now = self._now()
        for item in items:
            self._update_audit_attributes(item, do_created=False, now=now)
            for key, val in model_items(item):
                setattr(item, key, val)
        return items

    def upsert(self, data: ModelT) -> ModelT:
        """Update or create instance.

        Updates instance with the attribute values present on ``data``, or creates a new instance if
        one doesn't exist.

        Args:
            data: Instance to update existing, or be created. Identifier used to determine if an
                existing instance exists is the value of an attribute on `data` named as value of
                :attr:`id_attribute <AsyncGenericMockRepository.id_attribute>`.

        Returns:
            The updated or created instance.

        Raises:
            NotFoundError: If no instance found with same identifier as ``data``.
        """
        item_id = self.get_id_attribute_value(data)
        return self.update(data) if item_id in self.collection else self.add(data)

    def upsert_many(self, data: list[ModelT]) -> list[ModelT]:
        """Update or create multiple instance.

        Update instance with the attribute values present on ``data``, or create a new instance if
        one doesn't exist.

        Args:
            data: List of instances to update existing, or be created. Identifier used to determine if an
                existing instance exists is the value of an attribute on `data` named as value of
                :attr:`id_attribute <AsyncGenericMockRepository.id_attribute>`.

        Returns:
            The updated or created instances.
        """
        data_to_update = [row for row in data if self._find_or_none(self.get_id_attribute_value(row)) is not None]
        data_to_add = [row for row in data if self._find_or_none(self.get_id_attribute_value(row)) is None]

        updated_items = self.update_many(data_to_update)
        added_items = self.add_many(data_to_add)
        return updated_items + added_items

    def list_and_count(
        self,
        *filters: FilterTypes,
        **kwargs: Any,
    ) -> tuple[list[ModelT], int]:
        """Get a list of instances, optionally filtered with a total row count.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Instance attribute value filters.

        Returns:
            List of instances, and count of records returned by query, ignoring pagination.
        """
        return self.list(*filters, **kwargs), self.count(*filters, **kwargs)

    def list(self, *filters: FilterTypes, **kwargs: Any) -> list[ModelT]:
        """Get a list of instances, optionally filtered.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Instance attribute value filters.

        Returns:
            The list of instances, after filtering applied.
        """
        return list(self.filter_collection_by_kwargs(self.collection, **kwargs).values())

    def filter_collection_by_kwargs(  # type:ignore[override]
        self, collection: MutableMapping[Hashable, ModelT], /, **kwargs: Any
    ) -> MutableMapping[Hashable, ModelT]:
        """Filter the collection by kwargs.

        Args:
            collection: set of objects to filter
            **kwargs: key/value pairs such that objects remaining in the collection after filtering
                have the property that their attribute named ``key`` has value equal to ``value``.
        """
        new_collection: dict[Hashable, ModelT] = {}
        for item in self.collection.values():
            try:
                if all(getattr(item, name) == value for name, value in kwargs.items()):
                    new_collection[item.id] = item
            except AttributeError as orig:
                raise RepositoryError from orig
        return new_collection

    @classmethod
    def seed_collection(cls, instances: Iterable[ModelT]) -> None:
        """Seed the collection for repository type.

        Args:
            instances: the instances to be added to the collection.
        """
        for instance in instances:
            cls.collection[cls.get_id_attribute_value(instance)] = instance

    @classmethod
    def clear_collection(cls) -> None:
        """Empty the collection for repository type."""
        cls.collection = {}


def model_items(model: Any) -> list[tuple[str, Any]]:
    return [(k, v) for k, v in model.__dict__.items() if not k.startswith("_")]

from __future__ import annotations

from typing import TYPE_CHECKING, AbstractSet, Any, Iterable, MutableMapping, MutableSequence, Set, Tuple, cast

from typing_extensions import is_typeddict

from polyfactory.constants import INSTANTIABLE_TYPE_MAPPING, PY_38
from polyfactory.field_meta import FieldMeta
from polyfactory.utils.model_coverage import CoverageContainer

if TYPE_CHECKING:
    from polyfactory.factories.base import BaseFactory


def handle_collection_type(field_meta: FieldMeta, container_type: type, factory: type[BaseFactory[Any]]) -> Any:
    """Handle generation of container types recursively.

    :param container_type: A type that can accept type arguments.
    :param factory: A factory.
    :param field_meta: A field meta instance.

    :returns: A built result.
    """

    if PY_38 and container_type in INSTANTIABLE_TYPE_MAPPING:
        container_type = INSTANTIABLE_TYPE_MAPPING[container_type]  # type: ignore[assignment]

    container = container_type()
    if not field_meta.children:
        return container

    if issubclass(container_type, MutableMapping) or is_typeddict(container_type):
        for key_field_meta, value_field_meta in cast(
            Iterable[Tuple[FieldMeta, FieldMeta]],
            zip(field_meta.children[::2], field_meta.children[1::2]),
        ):
            key = factory.get_field_value(key_field_meta)
            value = factory.get_field_value(value_field_meta)
            container[key] = value
        return container

    if issubclass(container_type, MutableSequence):
        container.extend([factory.get_field_value(subfield_meta) for subfield_meta in field_meta.children])
        return container

    if issubclass(container_type, Set):
        for subfield_meta in field_meta.children:
            container.add(factory.get_field_value(subfield_meta))
        return container

    if issubclass(container_type, AbstractSet):
        return container.union(handle_collection_type(field_meta, set, factory))

    if issubclass(container_type, tuple):
        return container_type(map(factory.get_field_value, field_meta.children))

    msg = f"Unsupported container type: {container_type}"
    raise NotImplementedError(msg)


def handle_collection_type_coverage(
    field_meta: FieldMeta,
    container_type: type,
    factory: type[BaseFactory[Any]],
) -> Any:
    """Handle coverage generation of container types recursively.

    :param container_type: A type that can accept type arguments.
    :param factory: A factory.
    :param field_meta: A field meta instance.

    :returns: An unresolved built result.
    """
    container = container_type()
    if not field_meta.children:
        return container

    if issubclass(container_type, MutableMapping) or is_typeddict(container_type):
        for key_field_meta, value_field_meta in cast(
            Iterable[Tuple[FieldMeta, FieldMeta]],
            zip(field_meta.children[::2], field_meta.children[1::2]),
        ):
            key = CoverageContainer(factory.get_field_value_coverage(key_field_meta))
            value = CoverageContainer(factory.get_field_value_coverage(value_field_meta))
            container[key] = value
        return container

    if issubclass(container_type, MutableSequence):
        container_instance = container_type()
        for subfield_meta in field_meta.children:
            container_instance.extend(factory.get_field_value_coverage(subfield_meta))

        return container_instance

    if issubclass(container_type, Set):
        set_instance = container_type()
        for subfield_meta in field_meta.children:
            set_instance = set_instance.union(factory.get_field_value_coverage(subfield_meta))

        return set_instance

    if issubclass(container_type, AbstractSet):
        return container.union(handle_collection_type_coverage(field_meta, set, factory))

    if issubclass(container_type, tuple):
        return container_type(
            CoverageContainer(factory.get_field_value_coverage(subfield_meta)) for subfield_meta in field_meta.children
        )

    msg = f"Unsupported container type: {container_type}"
    raise NotImplementedError(msg)

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.utils.compat import async_next

__all__ = ("Dependency", "create_dependency_batches", "map_dependencies_recursively", "resolve_dependency")


if TYPE_CHECKING:
    from litestar._kwargs.cleanup import DependencyCleanupGroup
    from litestar.connection import ASGIConnection
    from litestar.di import Provide


class Dependency:
    """Dependency graph of a given combination of ``Route`` + ``RouteHandler``"""

    __slots__ = ("key", "provide", "dependencies")

    def __init__(self, key: str, provide: Provide, dependencies: list[Dependency]) -> None:
        """Initialize a dependency.

        Args:
            key: The dependency key
            provide: Provider
            dependencies: List of child nodes
        """
        self.key = key
        self.provide = provide
        self.dependencies = dependencies

    def __eq__(self, other: Any) -> bool:
        # check if memory address is identical, otherwise compare attributes
        return other is self or (isinstance(other, self.__class__) and other.key == self.key)

    def __hash__(self) -> int:
        return hash(self.key)


async def resolve_dependency(
    dependency: Dependency,
    connection: ASGIConnection,
    kwargs: dict[str, Any],
    cleanup_group: DependencyCleanupGroup,
) -> None:
    """Resolve a given instance of :class:`Dependency <litestar._kwargs.Dependency>`.

    All required sub dependencies must already
    be resolved into the kwargs. The result of the dependency will be stored in the kwargs.

    Args:
        dependency: An instance of :class:`Dependency <litestar._kwargs.Dependency>`
        connection: An instance of :class:`Request <litestar.connection.Request>` or
            :class:`WebSocket <litestar.connection.WebSocket>`.
        kwargs: Any kwargs to pass to the dependency, the result will be stored here as well.
        cleanup_group: DependencyCleanupGroup to which generators returned by ``dependency`` will be added
    """
    signature_model = dependency.provide.signature_model
    dependency_kwargs = (
        signature_model.parse_values_from_connection_kwargs(connection=connection, **kwargs)
        if signature_model._fields
        else {}
    )
    value = await dependency.provide(**dependency_kwargs)

    if dependency.provide.has_sync_generator_dependency:
        cleanup_group.add(value)
        value = next(value)
    elif dependency.provide.has_async_generator_dependency:
        cleanup_group.add(value)
        value = await async_next(value)

    kwargs[dependency.key] = value


def create_dependency_batches(expected_dependencies: set[Dependency]) -> list[set[Dependency]]:
    """Calculate batches for all dependencies, recursively.

    Args:
        expected_dependencies: A set of all direct :class:`Dependencies <litestar._kwargs.Dependency>`.

    Returns:
        A list of batches.
    """
    dependencies_to: dict[Dependency, set[Dependency]] = {}
    for dependency in expected_dependencies:
        if dependency not in dependencies_to:
            map_dependencies_recursively(dependency, dependencies_to)

    batches = []
    while dependencies_to:
        current_batch = {
            dependency
            for dependency, remaining_sub_dependencies in dependencies_to.items()
            if not remaining_sub_dependencies
        }

        for dependency in current_batch:
            del dependencies_to[dependency]
            for others_dependencies in dependencies_to.values():
                others_dependencies.discard(dependency)

        batches.append(current_batch)

    return batches


def map_dependencies_recursively(dependency: Dependency, dependencies_to: dict[Dependency, set[Dependency]]) -> None:
    """Recursively map dependencies to their sub dependencies.

    Args:
        dependency: The current dependency to map.
        dependencies_to: A map of dependency to its sub dependencies.
    """
    dependencies_to[dependency] = set(dependency.dependencies)
    for sub in dependency.dependencies:
        if sub not in dependencies_to:
            map_dependencies_recursively(sub, dependencies_to)

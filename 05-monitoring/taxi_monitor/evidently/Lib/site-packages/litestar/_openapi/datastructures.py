from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Iterator, Sequence

from litestar.exceptions import ImproperlyConfiguredException
from litestar.openapi.spec import Reference, Schema

if TYPE_CHECKING:
    from litestar.openapi import OpenAPIConfig
    from litestar.plugins import OpenAPISchemaPluginProtocol


class RegisteredSchema:
    """Object to store a schema and any references to it."""

    def __init__(self, key: tuple[str, ...], schema: Schema, references: list[Reference]) -> None:
        """Create a new RegisteredSchema object.

        Args:
            key: The key used to register the schema.
            schema: The schema object.
            references: A list of references to the schema.
        """
        self.key = key
        self.schema = schema
        self.references = references


class SchemaRegistry:
    """A registry for object schemas.

    This class is used to store schemas that we reference from other parts of the spec.

    Its main purpose is to allow us to generate the components/schemas section of the spec once we have
    collected all the schemas that should be included.

    This allows us to determine a path to the schema in the components/schemas section of the spec that
    is unique and as short as possible.
    """

    def __init__(self) -> None:
        self._schema_key_map: dict[tuple[str, ...], RegisteredSchema] = {}
        self._schema_reference_map: dict[int, RegisteredSchema] = {}
        self._model_name_groups: defaultdict[str, list[RegisteredSchema]] = defaultdict(list)

    def get_schema_for_key(self, key: tuple[str, ...]) -> Schema:
        """Get a registered schema by its key.

        Args:
            key: The key to the schema to get.

        Returns:
            A RegisteredSchema object.
        """
        if key not in self._schema_key_map:
            self._schema_key_map[key] = registered_schema = RegisteredSchema(key, Schema(), [])
            self._model_name_groups[key[-1]].append(registered_schema)
        return self._schema_key_map[key].schema

    def get_reference_for_key(self, key: tuple[str, ...]) -> Reference | None:
        """Get a reference to a registered schema by its key.

        Args:
            key: The key to the schema to get.

        Returns:
            A Reference object.
        """
        if key not in self._schema_key_map:
            return None
        registered_schema = self._schema_key_map[key]
        reference = Reference(f"#/components/schemas/{'_'.join(key)}")
        registered_schema.references.append(reference)
        self._schema_reference_map[id(reference)] = registered_schema
        return reference

    def from_reference(self, reference: Reference) -> RegisteredSchema:
        """Get a registered schema by its reference.

        Args:
            reference: The reference to the schema to get.

        Returns:
            A RegisteredSchema object.
        """
        return self._schema_reference_map[id(reference)]

    def __iter__(self) -> Iterator[RegisteredSchema]:
        """Iterate over the registered schemas."""
        return iter(self._schema_key_map.values())

    @staticmethod
    def set_reference_paths(name: str, registered_schema: RegisteredSchema) -> None:
        """Set the reference paths for a registered schema."""
        for reference in registered_schema.references:
            reference.ref = f"#/components/schemas/{name}"

    @staticmethod
    def remove_common_prefix(tuples: list[tuple[str, ...]]) -> list[tuple[str, ...]]:
        """Remove the common prefix from a list of tuples.

        Args:
            tuples: A list of tuples to remove the common prefix from.

        Returns:
            A list of tuples with the common prefix removed.
        """

        def longest_common_prefix(tuples_: list[tuple[str, ...]]) -> tuple[str, ...]:
            """Find the longest common prefix of a list of tuples.

            Args:
                tuples_: A list of tuples to find the longest common prefix of.

            Returns:
                The longest common prefix of the tuples.
            """
            prefix_ = tuples_[0]
            for t in tuples_:
                # Compare the current prefix with each tuple and shorten it
                prefix_ = prefix_[: min(len(prefix_), len(t))]
                for i in range(len(prefix_)):
                    if prefix_[i] != t[i]:
                        prefix_ = prefix_[:i]
                        break
            return prefix_

        prefix = longest_common_prefix(tuples)
        prefix_length = len(prefix)
        return [t[prefix_length:] for t in tuples]

    def generate_components_schemas(self) -> dict[str, Schema]:
        """Generate the components/schemas section of the spec.

        Returns:
            A dictionary of schemas.
        """
        components_schemas: dict[str, Schema] = {}

        for name, name_group in self._model_name_groups.items():
            if len(name_group) == 1:
                self.set_reference_paths(name, name_group[0])
                components_schemas[name] = name_group[0].schema
                continue

            full_keys = [registered_schema.key for registered_schema in name_group]
            names = ["_".join(k) for k in self.remove_common_prefix(full_keys)]
            for name_, registered_schema in zip(names, name_group):
                self.set_reference_paths(name_, registered_schema)
                components_schemas[name_] = registered_schema.schema

        # Sort them by name to ensure they're always generated in the same order.
        return {name: components_schemas[name] for name in sorted(components_schemas.keys())}


class OpenAPIContext:
    def __init__(
        self,
        openapi_config: OpenAPIConfig,
        plugins: Sequence[OpenAPISchemaPluginProtocol],
    ) -> None:
        self.openapi_config = openapi_config
        self.plugins = plugins
        self.operation_ids: set[str] = set()
        self.schema_registry = SchemaRegistry()

    def add_operation_id(self, operation_id: str) -> None:
        """Add an operation ID to the context.

        Args:
            operation_id: Operation ID to add.
        """
        if operation_id in self.operation_ids:
            raise ImproperlyConfiguredException(
                "operation_ids must be unique, "
                f"please ensure the value of 'operation_id' is either not set or unique for {operation_id}"
            )
        self.operation_ids.add(operation_id)

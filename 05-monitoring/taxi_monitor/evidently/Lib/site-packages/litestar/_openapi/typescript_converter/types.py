from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

__all__ = (
    "TypeScriptAnonymousInterface",
    "TypeScriptArray",
    "TypeScriptConst",
    "TypeScriptContainer",
    "TypeScriptElement",
    "TypeScriptEnum",
    "TypeScriptInterface",
    "TypeScriptIntersection",
    "TypeScriptLiteral",
    "TypeScriptNamespace",
    "TypeScriptPrimitive",
    "TypeScriptProperty",
    "TypeScriptType",
    "TypeScriptUnion",
)


def _as_string(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'

    if isinstance(value, bool):
        return "true" if value else "false"

    return "null" if value is None else str(value)


class TypeScriptElement(ABC):
    """A class representing a TypeScript type element."""

    @abstractmethod
    def write(self) -> str:
        """Write a typescript value corresponding to the given typescript element.

        Returns:
            A typescript string
        """
        raise NotImplementedError("")


class TypeScriptContainer(TypeScriptElement):
    """A class representing a TypeScript type container."""

    name: str

    @abstractmethod
    def write(self) -> str:
        """Write a typescript value corresponding to the given typescript container.

        Returns:
            A typescript string
        """
        raise NotImplementedError("")


@dataclass(unsafe_hash=True)
class TypeScriptIntersection(TypeScriptElement):
    """A class representing a TypeScript intersection type."""

    types: tuple[TypeScriptElement, ...]

    def write(self) -> str:
        """Write a typescript intersection value.

        Example:
            { prop: string } & { another: number }

        Returns:
            A typescript string
        """
        return " & ".join(t.write() for t in self.types)


@dataclass(unsafe_hash=True)
class TypeScriptUnion(TypeScriptElement):
    """A class representing a TypeScript union type."""

    types: tuple[TypeScriptElement, ...]

    def write(self) -> str:
        """Write a typescript union value.

        Example:
            string | number

        Returns:
            A typescript string
        """
        return " | ".join(sorted(t.write() for t in self.types))


@dataclass(unsafe_hash=True)
class TypeScriptPrimitive(TypeScriptElement):
    """A class representing a TypeScript primitive type."""

    type: Literal[
        "string", "number", "boolean", "any", "null", "undefined", "symbol", "Record<string, unknown>", "unknown[]"
    ]

    def write(self) -> str:
        """Write a typescript primitive type.

        Example:
            null

        Returns:
            A typescript string
        """
        return self.type


@dataclass(unsafe_hash=True)
class TypeScriptLiteral(TypeScriptElement):
    """A class representing a TypeScript literal type."""

    value: str | int | float | bool | None

    def write(self) -> str:
        """Write a typescript literal type.

        Example:
            "someValue"

        Returns:
            A typescript string
        """
        return _as_string(self.value)


@dataclass(unsafe_hash=True)
class TypeScriptArray(TypeScriptElement):
    """A class representing a TypeScript array type."""

    item_type: TypeScriptElement

    def write(self) -> str:
        """Write a typescript array type.

        Example:
            number[]

        Returns:
            A typescript string
        """
        value = (
            f"({self.item_type.write()})"
            if isinstance(self.item_type, (TypeScriptUnion, TypeScriptIntersection))
            else self.item_type.write()
        )
        return f"{value}[]"


@dataclass(unsafe_hash=True)
class TypeScriptProperty(TypeScriptElement):
    """A class representing a TypeScript interface property."""

    required: bool
    key: str
    value: TypeScriptElement

    def write(self) -> str:
        """Write a typescript property. This class is used exclusively inside interfaces.

        Example:
            key: string;
            optional?: number;

        Returns:
            A typescript string
        """
        return f"{self.key}{':' if self.required else '?:'} {self.value.write()};"


@dataclass(unsafe_hash=True)
class TypeScriptAnonymousInterface(TypeScriptElement):
    """A class representing a TypeScript anonymous interface."""

    properties: tuple[TypeScriptProperty, ...]

    def write(self) -> str:
        """Write a typescript interface object, without a name.

        Example:
            {
                key: string;
                optional?: number;
            }

        Returns:
            A typescript string
        """
        props = "\t" + "\n\t".join([prop.write() for prop in sorted(self.properties, key=lambda prop: prop.key)])
        return f"{{\n{props}\n}}"


@dataclass(unsafe_hash=True)
class TypeScriptInterface(TypeScriptContainer):
    """A class representing a TypeScript interface."""

    name: str
    properties: tuple[TypeScriptProperty, ...]

    def write(self) -> str:
        """Write a typescript interface.

        Example:
            export interface MyInterface {
                key: string;
                optional?: number;
            };

        Returns:
            A typescript string
        """
        interface = TypeScriptAnonymousInterface(properties=self.properties)
        return f"export interface {self.name} {interface.write()};"


@dataclass(unsafe_hash=True)
class TypeScriptEnum(TypeScriptContainer):
    """A class representing a TypeScript enum."""

    name: str
    values: tuple[tuple[str, str], ...] | tuple[tuple[str, int | float], ...]

    def write(self) -> str:
        """Write a typescript enum.

        Example:
            export enum MyEnum {
                DOG = "canine",
                CAT = "feline",
            };

        Returns:
            A typescript string
        """
        members = "\t" + "\n\t".join(
            [f"{key} = {_as_string(value)}," for key, value in sorted(self.values, key=lambda member: member[0])]
        )
        return f"export enum {self.name} {{\n{members}\n}};"


@dataclass(unsafe_hash=True)
class TypeScriptType(TypeScriptContainer):
    """A class representing a TypeScript type."""

    name: str
    value: TypeScriptElement

    def write(self) -> str:
        """Write a typescript type.

        Example:
            export type MyType = number | "42";

        Returns:
            A typescript string
        """
        return f"export type {self.name} = {self.value.write()};"


@dataclass(unsafe_hash=True)
class TypeScriptConst(TypeScriptContainer):
    """A class representing a TypeScript const."""

    name: str
    value: TypeScriptPrimitive | TypeScriptLiteral

    def write(self) -> str:
        """Write a typescript const.

        Example:
            export const MyConst: number;

        Returns:
            A typescript string
        """
        return f"export const {self.name}: {self.value.write()};"


@dataclass(unsafe_hash=True)
class TypeScriptNamespace(TypeScriptContainer):
    """A class representing a TypeScript namespace."""

    name: str
    values: tuple[TypeScriptContainer, ...]

    def write(self) -> str:
        """Write a typescript namespace.

        Example:
            export MyNamespace {
                export const MyConst: number;
            }

        Returns:
            A typescript string
        """
        members = "\t" + "\n\n\t".join([value.write() for value in sorted(self.values, key=lambda el: el.name)])
        return f"export namespace {self.name} {{\n{members}\n}};"

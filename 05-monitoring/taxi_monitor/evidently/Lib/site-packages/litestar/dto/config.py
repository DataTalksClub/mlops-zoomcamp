from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from litestar.exceptions import ImproperlyConfiguredException

if TYPE_CHECKING:
    from typing import AbstractSet

    from litestar.dto.types import RenameStrategy

__all__ = ("DTOConfig",)


@dataclass(frozen=True)
class DTOConfig:
    """Control the generated DTO."""

    exclude: AbstractSet[str] = field(default_factory=set)
    """Explicitly exclude fields from the generated DTO.

    If exclude is specified, all fields not specified in exclude will be included by default.

    Notes:
        - The field names are dot-separated paths to nested fields, e.g. ``"address.street"`` will
            exclude the ``"street"`` field from a nested ``"address"`` model.
        - 'exclude' mutually exclusive with 'include' - specifying both values will raise an
            ``ImproperlyConfiguredException``.
    """
    include: AbstractSet[str] = field(default_factory=set)
    """Explicitly include fields in the generated DTO.

    If include is specified, all fields not specified in include will be excluded by default.

    Notes:
        - The field names are dot-separated paths to nested fields, e.g. ``"address.street"`` will
            include the ``"street"`` field from a nested ``"address"`` model.
        - 'include' mutually exclusive with 'exclude' - specifying both values will raise an
            ``ImproperlyConfiguredException``.
    """
    rename_fields: dict[str, str] = field(default_factory=dict)
    """Mapping of field names, to new name."""
    rename_strategy: RenameStrategy | None = None
    """Rename all fields using a pre-defined strategy or a custom strategy.

    The pre-defined strategies are: `upper`, `lower`, `camel`, `pascal`.

    A custom strategy is any callable that accepts a string as an argument and
    return a string.

    Fields defined in ``rename_fields`` are ignored."""
    max_nested_depth: int = 1
    """The maximum depth of nested items allowed for data transfer."""
    partial: bool = False
    """Allow transfer of partial data."""
    underscore_fields_private: bool = True
    """Fields starting with an underscore are considered private and excluded from data transfer."""
    experimental_codegen_backend: bool | None = None
    """Use the experimental codegen backend"""

    def __post_init__(self) -> None:
        if self.include and self.exclude:
            raise ImproperlyConfiguredException(
                "'include' and 'exclude' are mutually exclusive options, please use one of them"
            )

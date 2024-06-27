from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from litestar.enums import MediaType

if TYPE_CHECKING:
    from litestar.openapi.spec import Example
    from litestar.types import DataContainerType


__all__ = ("ResponseSpec",)


@dataclass
class ResponseSpec:
    """Container type of additional responses."""

    data_container: DataContainerType | None
    """A model that describes the content of the response."""
    generate_examples: bool = field(default=True)
    """Generate examples for the response content."""
    description: str = field(default="Additional response")
    """A description of the response."""
    media_type: MediaType = field(default=MediaType.JSON)
    """Response media type."""
    examples: list[Example] | None = field(default=None)
    """A list of Example models."""

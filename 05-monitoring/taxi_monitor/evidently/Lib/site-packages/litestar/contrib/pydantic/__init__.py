from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.plugins import InitPluginProtocol

from .pydantic_di_plugin import PydanticDIPlugin
from .pydantic_dto_factory import PydanticDTO
from .pydantic_init_plugin import PydanticInitPlugin
from .pydantic_schema_plugin import PydanticSchemaPlugin

if TYPE_CHECKING:
    from pydantic import BaseModel
    from pydantic.v1 import BaseModel as BaseModelV1

    from litestar.config.app import AppConfig

__all__ = (
    "PydanticDTO",
    "PydanticInitPlugin",
    "PydanticSchemaPlugin",
    "PydanticPlugin",
    "PydanticDIPlugin",
)


def _model_dump(model: BaseModel | BaseModelV1, *, by_alias: bool = False) -> dict[str, Any]:
    return (
        model.model_dump(mode="json", by_alias=by_alias)  # pyright: ignore
        if hasattr(model, "model_dump")
        else {k: v.decode() if isinstance(v, bytes) else v for k, v in model.dict(by_alias=by_alias).items()}
    )


def _model_dump_json(model: BaseModel | BaseModelV1, by_alias: bool = False) -> str:
    return (
        model.model_dump_json(by_alias=by_alias)  # pyright: ignore
        if hasattr(model, "model_dump_json")
        else model.json(by_alias=by_alias)  # pyright: ignore
    )


class PydanticPlugin(InitPluginProtocol):
    """A plugin that provides Pydantic integration."""

    __slots__ = ("prefer_alias",)

    def __init__(self, prefer_alias: bool = False) -> None:
        """Initialize ``PydanticPlugin``.

        Args:
            prefer_alias: OpenAPI and ``type_encoders`` will export by alias
        """
        self.prefer_alias = prefer_alias

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Configure application for use with Pydantic.

        Args:
            app_config: The :class:`AppConfig <.config.app.AppConfig>` instance.
        """
        app_config.plugins.extend(
            [
                PydanticInitPlugin(prefer_alias=self.prefer_alias),
                PydanticSchemaPlugin(prefer_alias=self.prefer_alias),
                PydanticDIPlugin(),
            ]
        )
        return app_config

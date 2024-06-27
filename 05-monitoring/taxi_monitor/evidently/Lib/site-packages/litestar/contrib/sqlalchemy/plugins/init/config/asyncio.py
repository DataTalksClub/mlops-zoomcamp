from __future__ import annotations

from advanced_alchemy.config.asyncio import AlembicAsyncConfig, AsyncSessionConfig
from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import (
    SQLAlchemyAsyncConfig as _SQLAlchemyAsyncConfig,
)
from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import (
    autocommit_before_send_handler,
    default_before_send_handler,
)
from sqlalchemy.ext.asyncio import AsyncEngine

from litestar.contrib.sqlalchemy.plugins.init.config.compat import _CreateEngineMixin

__all__ = (
    "SQLAlchemyAsyncConfig",
    "AlembicAsyncConfig",
    "AsyncSessionConfig",
    "default_before_send_handler",
    "autocommit_before_send_handler",
)


class SQLAlchemyAsyncConfig(_SQLAlchemyAsyncConfig, _CreateEngineMixin[AsyncEngine]): ...

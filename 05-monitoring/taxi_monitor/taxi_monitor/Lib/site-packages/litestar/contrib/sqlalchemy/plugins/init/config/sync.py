from __future__ import annotations

from advanced_alchemy.config.sync import AlembicSyncConfig, SyncSessionConfig
from advanced_alchemy.extensions.litestar.plugins.init.config.sync import (
    SQLAlchemySyncConfig as _SQLAlchemySyncConfig,
)
from advanced_alchemy.extensions.litestar.plugins.init.config.sync import (
    autocommit_before_send_handler,
    default_before_send_handler,
)
from sqlalchemy import Engine

from litestar.contrib.sqlalchemy.plugins.init.config.compat import _CreateEngineMixin

__all__ = (
    "SQLAlchemySyncConfig",
    "AlembicSyncConfig",
    "SyncSessionConfig",
    "default_before_send_handler",
    "autocommit_before_send_handler",
)


class SQLAlchemySyncConfig(_SQLAlchemySyncConfig, _CreateEngineMixin[Engine]): ...

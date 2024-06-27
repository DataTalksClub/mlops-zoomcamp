from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Protocol, TypeVar

from litestar.utils.deprecation import deprecated

if TYPE_CHECKING:
    from sqlalchemy import Engine
    from sqlalchemy.ext.asyncio import AsyncEngine


EngineT_co = TypeVar("EngineT_co", bound="Engine | AsyncEngine", covariant=True)


class HasGetEngine(Protocol[EngineT_co]):
    def get_engine(self) -> EngineT_co: ...


class _CreateEngineMixin(Generic[EngineT_co]):
    @deprecated(version="2.1.1", removal_in="3.0.0", alternative="get_engine()")
    def create_engine(self: HasGetEngine[EngineT_co]) -> EngineT_co:
        return self.get_engine()

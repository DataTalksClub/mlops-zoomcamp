from abc import ABC
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Dict
from typing import Generic
from typing import List
from typing import Type
from typing import TypeVar

from litestar import Litestar
from litestar import Router
from litestar.di import Provide
from litestar.types import ControllerRouterHandler
from litestar.types import ExceptionHandlersMap
from litestar.types import Middleware

from evidently._pydantic_compat import Extra
from evidently.pydantic_utils import PolymorphicModel
from evidently.ui.utils import parse_json

SECTION_COMPONENT_TYPE_MAPPING: Dict[str, Type["Component"]] = {}


T = TypeVar("T", bound="Component")


class AppBuilder:
    def __init__(self, context: "ComponentContext"):
        self.context = context
        self.dependencies: Dict[str, Provide] = {}
        self.route_handlers: List[ControllerRouterHandler] = []
        self.api_route_handlers: List[ControllerRouterHandler] = []
        self.exception_handlers: ExceptionHandlersMap = {}
        self.middlewares: List[Middleware] = []
        self.kwargs: Dict[str, Any] = {}

    def build_api_router(self):
        return Router(path="/api", route_handlers=self.api_route_handlers)

    def build(self) -> Litestar:
        api_router = self.build_api_router()
        return Litestar(
            route_handlers=[api_router] + self.route_handlers,
            exception_handlers=self.exception_handlers,
            dependencies=self.dependencies,
            middleware=self.middlewares,
            **self.kwargs,
        )


class ComponentContext:
    def get_component(self, type_: Type[T]) -> T:
        raise NotImplementedError


class Component(PolymorphicModel, ABC):
    __section__: ClassVar[str] = ""
    __require__: ClassVar[List[Type["Component"]]] = []

    def get_requirements(self) -> List[Type["Component"]]:
        return self.__require__

    class Config:
        extra = Extra.forbid

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.__section__:
            SECTION_COMPONENT_TYPE_MAPPING[cls.__section__] = cls

    def get_dependencies(self, ctx: ComponentContext) -> Dict[str, Provide]:
        return {}

    def get_middlewares(self, ctx: ComponentContext):
        return []

    def get_route_handlers(self, ctx: ComponentContext):
        return []

    def get_api_route_handelers(self, ctx: ComponentContext):
        return []

    def apply(self, ctx: ComponentContext, builder: AppBuilder):
        builder.dependencies.update(self.get_dependencies(ctx))
        builder.middlewares.extend(self.get_middlewares(ctx))
        builder.route_handlers.extend(self.get_route_handlers(ctx))
        builder.api_route_handlers.extend(self.get_api_route_handelers(ctx))

    def finalize(self, ctx: ComponentContext, app: Litestar):
        pass


DT = TypeVar("DT")


class FactoryComponent(Component, Generic[DT], ABC):
    dependency_name: ClassVar[str]
    use_cache: ClassVar[bool] = True
    sync_to_thread: ClassVar[bool] = False

    def dependency_factory(self) -> Callable[..., DT]:
        raise NotImplementedError(self.__class__)

    def get_dependencies(self, ctx: ComponentContext) -> Dict[str, Provide]:
        return {
            self.dependency_name: Provide(
                self.dependency_factory(), use_cache=self.use_cache, sync_to_thread=self.sync_to_thread
            )
        }


class ServiceComponent(Component):
    host: str = "0.0.0.0"
    port: int = 8000

    def get_dependencies(self, ctx: ComponentContext) -> Dict[str, Provide]:
        # todo: maybe not put utils here
        return {
            "parsed_json": Provide(parse_json, sync_to_thread=False),
        }

import contextlib
from typing import Dict
from typing import Iterator
from typing import List
from typing import Type
from typing import TypeVar

import dynaconf
from dynaconf import LazySettings
from dynaconf.utils.boxing import DynaBox
from litestar import Litestar
from litestar.di import Provide

from evidently._pydantic_compat import BaseModel
from evidently._pydantic_compat import PrivateAttr
from evidently._pydantic_compat import parse_obj_as
from evidently.ui.components.base import SECTION_COMPONENT_TYPE_MAPPING
from evidently.ui.components.base import AppBuilder
from evidently.ui.components.base import Component
from evidently.ui.components.base import ComponentContext
from evidently.ui.components.base import ServiceComponent
from evidently.ui.components.base import T
from evidently.ui.components.security import SecurityComponent


def _convert_keys(box):
    if isinstance(box, (DynaBox, LazySettings)):
        return {k.lower(): _convert_keys(v) for k, v in box.items()}
    return box


class ConfigContext(ComponentContext):
    def __init__(self, config: "Config", components_mapping: Dict[Type[Component], Component]):
        self.config = config
        self.components_mapping = components_mapping

    def get_component(self, type_: Type[T]) -> T:
        for cls in self.components_mapping:
            if issubclass(cls, type_):
                return self.components_mapping[cls]
        raise ValueError(f"Component of type {type_.__name__} not found")

    @property
    def components(self) -> List[Component]:
        return list(self.components_mapping.values())

    def get_dependencies(self) -> Dict[str, Provide]:
        res = {}
        for c in self.components:
            dependencies = c.get_dependencies(self)
            print(f"{c.__class__.__name__} deps: " + ", ".join(dependencies))
            res.update(dependencies)
        return res

    def get_middlewares(self):
        res = []
        for c in self.components:
            res.extend(c.get_middlewares(self))
        return res

    def apply(self, builder: AppBuilder):
        for c in self.components:
            c.apply(self, builder)

    def finalize(self, app: Litestar):
        for c in self.components:
            c.finalize(self, app)

    def validate(self):
        for c in self.components_mapping.values():
            reqs = c.get_requirements()
            for r in reqs:
                try:
                    self.get_component(r)
                except ValueError as e:
                    raise ValueError(f"Component {c.__class__.__name__} missing {r.__name__} requirement") from e


class Config(BaseModel):
    additional_components: Dict[str, Component] = {}

    _components: List[Component] = PrivateAttr(default_factory=list)
    _ctx: ComponentContext = PrivateAttr()

    @property
    def components(self) -> List[Component]:
        return [getattr(self, name) for name in self.__fields__ if isinstance(getattr(self, name), Component)] + list(
            self.additional_components.values()
        )

    @contextlib.contextmanager
    def context(self) -> Iterator[ConfigContext]:
        ctx = ConfigContext(self, {type(c): c for c in self.components})
        ctx.validate()
        self._ctx = ctx
        yield ctx
        del self._ctx


class AppConfig(Config):
    security: SecurityComponent
    service: ServiceComponent


TConfig = TypeVar("TConfig", bound=Config)


def load_config(config_type: Type[TConfig], box: dict) -> TConfig:
    new_box = _convert_keys(box)
    components = {}
    named_components = {}
    for section, component_dict in new_box.items():
        # todo
        if not isinstance(component_dict, dict):
            continue
        if section.endswith("for_dynaconf"):
            continue
        if section in ("renamed_vars", "dict_itemiterator"):
            continue
        if section in config_type.__fields__:
            component = parse_obj_as(config_type.__fields__[section].type_, component_dict)
            named_components[section] = component
        elif section in SECTION_COMPONENT_TYPE_MAPPING:
            component = parse_obj_as(SECTION_COMPONENT_TYPE_MAPPING[section], component_dict)
            components[section] = component
        else:
            raise ValueError(f"unknown config section {section}")

    # todo: we will get validation error if not all components configured, but we can wrap it more nicely
    return config_type(additional_components=components, **named_components)


def load_config_from_file(cls: Type[TConfig], path: str, envvar_prefix: str = "EVIDENTLY") -> TConfig:
    dc = dynaconf.Dynaconf(
        envvar_prefix=envvar_prefix,
    )
    dc.configure(settings_module=path)
    config = load_config(cls, dc)
    return config


settings = dynaconf.Dynaconf(
    envvar_prefix="EVIDENTLY",
)

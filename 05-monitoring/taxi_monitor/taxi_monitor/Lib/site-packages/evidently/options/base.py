from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from evidently._pydantic_compat import BaseModel
from evidently.options import ColorOptions
from evidently.options.agg_data import DataDefinitionOptions
from evidently.options.agg_data import RenderOptions
from evidently.options.option import Option

TypeParam = TypeVar("TypeParam", bound=Option)


class Options(BaseModel):
    color: Optional[ColorOptions] = None
    render: Optional[RenderOptions] = None
    custom: Dict[Type[Option], Option] = {}
    data_definition: Optional[DataDefinitionOptions] = None

    @property
    def color_options(self) -> ColorOptions:
        return self.color or ColorOptions()

    @property
    def render_options(self) -> RenderOptions:
        return self.render or RenderOptions()

    @property
    def data_definition_options(self) -> DataDefinitionOptions:
        return self.data_definition or DataDefinitionOptions()

    def get(self, option_type: Type[TypeParam]) -> TypeParam:
        if option_type in _option_cls_mapping:
            res = getattr(self, _option_cls_mapping[option_type])
            if res is None:
                return option_type()
            return res
        if option_type in self.custom:
            return self.custom[option_type]  # type: ignore[return-value]
        return option_type()

    @classmethod
    def from_list(cls, values: List[Option]) -> "Options":
        kwargs: Dict = {"custom": {}}
        for value in values:
            field = _option_cls_mapping.get(type(value), None)
            if field is not None:
                kwargs[field] = value
            else:
                kwargs["custom"][type(value)] = value
        return Options(**kwargs)

    @classmethod
    def from_any_options(cls, options: "AnyOptions") -> "Options":
        """Options can be provided as Options object, list of Option classes or raw dict"""
        _options = None
        if isinstance(options, dict):
            _options = Options(**options)
        if isinstance(options, list):
            _options = Options.from_list(options)
        if isinstance(options, Options):
            _options = options

        return _options or Options()

    def override(self, other: "Options") -> "Options":
        res = Options()
        res.custom = self.custom.copy()
        for key, value in other.custom.items():
            res.custom[key] = value
        for name in self.__fields__:
            if name == "custom":
                continue
            override = getattr(other, name)
            if override is None:
                override = getattr(self, name)
            setattr(res, name, override)

        return res

    def __hash__(self):
        value_pairs = [(f, getattr(self, f)) for f in self.__fields__ if f != "custom"]
        value_pairs.extend(sorted(list(self.custom.items())))
        return hash((type(self),) + tuple(value_pairs))


_option_cls_mapping = {field.type_: name for name, field in Options.__fields__.items()}

AnyOptions = Union[Options, dict, List[Option], None]

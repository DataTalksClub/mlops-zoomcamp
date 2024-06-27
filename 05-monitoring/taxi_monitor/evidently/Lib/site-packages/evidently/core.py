from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import Iterator
from typing import Optional
from typing import Set
from typing import Type
from typing import TypeVar
from typing import Union
from typing import get_args

import numpy as np
import pandas as pd

from evidently._pydantic_compat import SHAPE_DICT
from evidently._pydantic_compat import SHAPE_LIST
from evidently._pydantic_compat import SHAPE_SET
from evidently._pydantic_compat import SHAPE_TUPLE
from evidently._pydantic_compat import ModelField
from evidently.pydantic_utils import IncludeTags
from evidently.pydantic_utils import pydantic_type_validator

if TYPE_CHECKING:
    from evidently._pydantic_compat import AbstractSetIntStr
    from evidently._pydantic_compat import MappingIntStrAny

from enum import Enum

from evidently._pydantic_compat import BaseConfig
from evidently._pydantic_compat import BaseModel

IncludeOptions = Union["AbstractSetIntStr", "MappingIntStrAny"]


class ColumnType(Enum):
    Numerical = "num"
    Categorical = "cat"
    Text = "text"
    Datetime = "datetime"
    Date = "data"
    Id = "id"
    Unknown = "unknown"


def _is_mapping_field(field: ModelField):
    return field.shape in (SHAPE_DICT,)


def _is_sequence_field(field: ModelField):
    return field.shape in (SHAPE_LIST, SHAPE_SET, SHAPE_TUPLE)


# workaround for https://github.com/pydantic/pydantic/issues/5301
class AllDict(dict):
    def __init__(self, value):
        super().__init__()
        self._value = value

    def __contains__(self, item):
        return True

    def get(self, __key):
        return self._value

    def __repr__(self):
        return f"{{'__all__':{self._value}}}"

    def __bool__(self):
        return True


@pydantic_type_validator(pd.Series)
def series_validator(value):
    return pd.Series(value)


@pydantic_type_validator(pd.DataFrame)
def dataframe_validator(value):
    return pd.DataFrame(value)


# @pydantic_type_validator(pd.Index)
# def index_validator(value):
#     return pd.Index(value)


@pydantic_type_validator(np.double)
def np_inf_valudator(value):
    return np.float(value)


@pydantic_type_validator(np.ndarray)
def np_array_valudator(value):
    return np.array(value)


class BaseResult(BaseModel):
    class Config(BaseConfig):
        arbitrary_types_allowed = True
        dict_include: bool = True
        pd_include: bool = True
        pd_name_mapping: Dict[str, str] = {}

        dict_include_fields: set = set()
        dict_exclude_fields: set = set()
        pd_include_fields: set = set()
        pd_exclude_fields: set = set()

        tags: Set[IncludeTags] = set()
        field_tags: Dict[str, set] = {}
        extract_as_obj: bool = False

    if TYPE_CHECKING:
        __config__: ClassVar[Type[Config]] = Config

    def get_dict(
        self,
        include_render: bool = False,
        include: Optional[IncludeOptions] = None,
        exclude: Optional[IncludeOptions] = None,
    ):
        exclude_tags = {IncludeTags.TypeField}
        if not include_render:
            exclude_tags.add(IncludeTags.Render)
        return self.dict(include=include or self._build_include(exclude_tags=exclude_tags), exclude=exclude)

    def _build_include(
        self,
        exclude_tags: Set[IncludeTags],
        include=None,
    ) -> "MappingIntStrAny":
        if not self.__config__.dict_include and not include or any(t in exclude_tags for t in self.__config__.tags):
            return {}
        include = include or {}
        dict_include_fields = (
            set(() if isinstance(include, bool) else include)
            or self.__config__.dict_include_fields
            or set(self.__fields__.keys())
        )
        dict_exclude_fields = self.__config__.dict_exclude_fields or set()
        field_tags = get_all_fields_tags(self.__class__)
        result: Dict[str, Any] = {}
        for name, field in self.__fields__.items():
            if field_tags.get(name) and any(tag in exclude_tags for tag in field_tags.get(name, set())):
                continue
            if isinstance(field.type_, type) and issubclass(field.type_, BaseResult):
                if (
                    (not field.type_.__config__.dict_include or name in dict_exclude_fields)
                    and not field.field_info.include
                    and name not in include
                ):
                    continue

                field_value = getattr(self, name)
                if field_value is None:
                    build_include = {}
                elif _is_mapping_field(field):
                    build_include = {
                        k: v._build_include(
                            exclude_tags=exclude_tags, include=field.field_info.include or include.get(name, {})
                        )
                        for k, v in field_value.items()
                    }
                elif _is_sequence_field(field):
                    build_include = {
                        i: v._build_include(
                            exclude_tags=exclude_tags, include=field.field_info.include or include.get(name, {})
                        )
                        for i, v in enumerate(field_value)
                    }
                else:
                    build_include = field_value._build_include(
                        exclude_tags=exclude_tags, include=field.field_info.include or include.get(name, {})
                    )
                result[name] = build_include
                continue
            if name in dict_exclude_fields and name not in include:
                continue
            if name not in dict_include_fields:
                continue
            result[name] = True
        return result  # type: ignore

    def __init_subclass__(cls, **kwargs):
        cls.__include_fields__ = None

    def collect_pandas_columns(self, prefix="", include: Set[str] = None, exclude: Set[str] = None) -> Dict[str, Any]:
        include = include or self.__config__.pd_include_fields or set(self.__fields__)
        exclude = exclude or self.__config__.pd_exclude_fields or set()

        data = {}
        field_tags = self.__config__.field_tags
        for name, field in self.__fields__.items():
            if field_tags.get(name) and any(
                ft in {IncludeTags.TypeField, IncludeTags.Render} for ft in field_tags.get(name, set())
            ):
                continue
            if name not in include or name in exclude:
                continue
            field_value = getattr(self, name)
            field_prefix = f"{prefix}{self.__config__.pd_name_mapping.get(name, name)}_"
            if isinstance(field_value, BaseResult):
                field_type = type(field_value)
                if field_type.__config__.pd_include:
                    if field_value is None:
                        continue
                    if isinstance(field_value, BaseResult):
                        data.update(field_value.collect_pandas_columns(field_prefix))
                continue
            if isinstance(field_value, dict):
                # todo: deal with more complex stuff later
                if all(isinstance(v, BaseResult) for v in field_value.values()):
                    raise NotImplementedError(
                        f"{self.__class__.__name__} does not support dataframe rendering. Please submit an issue to https://github.com/evidentlyai/evidently/issues"
                    )
                dict_value: BaseResult
                for dict_key, dict_value in field_value.items():
                    for (
                        key,
                        value,
                    ) in dict_value.collect_pandas_columns().items():
                        data[f"{field_prefix}_{dict_key}_{key}"] = value
                continue
            data[prefix + name] = field_value
        return data

    def get_pandas(self) -> pd.DataFrame:
        return pd.DataFrame([self.collect_pandas_columns()])


T = TypeVar("T")


def _get_actual_type(cls: Type[T]) -> Type[T]:
    if isinstance(cls, type):
        return cls
    if cls is Any:
        return type
    return _get_actual_type(get_args(cls)[0])


def _iterate_base_result_types(cls: Type[BaseModel]) -> Iterator[Type[BaseResult]]:
    for type_ in cls.__mro__:
        if not issubclass(type_, BaseResult):
            return
        yield type_


def get_cls_tags(cls: Type[BaseModel]) -> Set[IncludeTags]:
    if issubclass(cls, BaseResult):
        return cls.__config__.tags
    return set()


def get_field_tags(cls: Type[BaseModel], field_name: str) -> Set[IncludeTags]:
    field_tags = set()
    for type_ in _iterate_base_result_types(cls):
        if field_name not in type_.__config__.field_tags:
            continue
        field_tags = type_.__config__.field_tags[field_name]
        break

    field = cls.__fields__[field_name]
    field_type = _get_actual_type(field.type_)
    self_tags = set() if not issubclass(cls, BaseResult) else cls.__config__.tags
    cls_tags = get_cls_tags(field_type)
    return self_tags.union(field_tags).union(cls_tags)


def get_all_fields_tags(cls: Type[BaseResult]) -> Dict[str, Set[IncludeTags]]:
    return {field_name: get_field_tags(cls, field_name) for field_name in cls.__fields__}

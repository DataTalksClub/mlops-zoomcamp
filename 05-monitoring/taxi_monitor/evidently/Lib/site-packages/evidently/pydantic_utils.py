import dataclasses
import hashlib
import itertools
import json
import os
import warnings
from enum import Enum
from functools import lru_cache
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import FrozenSet
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union
from typing import get_args

from typing_inspect import is_union_type

from evidently._pydantic_compat import SHAPE_DICT
from evidently._pydantic_compat import BaseModel
from evidently._pydantic_compat import Field
from evidently._pydantic_compat import ModelMetaclass
from evidently._pydantic_compat import import_string

if TYPE_CHECKING:
    from evidently._pydantic_compat import DictStrAny
T = TypeVar("T")


def pydantic_type_validator(type_: Type[Any]):
    def decorator(f):
        from evidently._pydantic_compat import _VALIDATORS

        for cls, validators in _VALIDATORS:
            if cls is type_:
                validators.append(f)
                return

        _VALIDATORS.append(
            (type_, [f]),
        )

    return decorator


class FrozenBaseMeta(ModelMetaclass):
    def __new__(mcs, name, bases, namespace, **kwargs):
        res = super().__new__(mcs, name, bases, namespace, **kwargs)
        res.__config__.frozen = True
        return res


object_setattr = object.__setattr__
object_delattr = object.__delattr__


class FrozenBaseModel(BaseModel, metaclass=FrozenBaseMeta):
    class Config:
        underscore_attrs_are_private = True

    _init_values: Optional[Dict]

    def __init__(self, **data: Any):
        super().__init__(**self.__init_values__, **data)
        for private_attr in self.__private_attributes__:
            if private_attr in self.__init_values__:
                object_setattr(self, private_attr, self.__init_values__[private_attr])
        object_setattr(self, "_init_values", None)

    @property
    def __init_values__(self):
        if not hasattr(self, "_init_values"):
            object_setattr(self, "_init_values", {})
        return self._init_values

    def __setattr__(self, key, value):
        if self.__init_values__ is not None:
            if key not in self.__fields__ and key not in self.__private_attributes__:
                raise AttributeError(f"{self.__class__.__name__} has no attribute {key}")
            self.__init_values__[key] = value
            return
        super().__setattr__(key, value)

    def __hash__(self):
        try:
            return hash(self.__class__) + hash(tuple(self._field_hash(v) for v in self.__dict__.values()))
        except TypeError:
            raise

    @classmethod
    def _field_hash(cls, value):
        if isinstance(value, list):
            return tuple(cls._field_hash(v) for v in value)
        if isinstance(value, dict):
            return tuple((k, cls._field_hash(v)) for k, v in value.items())
        return value


def all_subclasses(cls: Type[T]) -> Set[Type[T]]:
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])


ALLOWED_TYPE_PREFIXES = ["evidently."]

EVIDENTLY_TYPE_PREFIXES_ENV = "EVIDENTLY_TYPE_PREFIXES"
ALLOWED_TYPE_PREFIXES.extend([p for p in os.environ.get(EVIDENTLY_TYPE_PREFIXES_ENV, "").split(",") if p])

TYPE_ALIASES: Dict[Tuple[Type["PolymorphicModel"], str], str] = {}
LOADED_TYPE_ALIASES: Dict[Tuple[Type["PolymorphicModel"], str], Type["PolymorphicModel"]] = {}


def register_type_alias(base_class: Type["PolymorphicModel"], classpath: str, alias: str):
    key = (base_class, alias)

    if key in TYPE_ALIASES and TYPE_ALIASES[key] != classpath:
        warnings.warn(f"Duplicate key {key} in alias map")
    TYPE_ALIASES[key] = classpath


def register_loaded_alias(base_class: Type["PolymorphicModel"], cls: Type["PolymorphicModel"], alias: str):
    if not issubclass(cls, base_class):
        raise ValueError(f"Cannot register alias: {cls.__name__} is not subclass of {base_class.__name__}")

    key = (base_class, alias)
    if key in LOADED_TYPE_ALIASES and LOADED_TYPE_ALIASES[key] != cls:
        warnings.warn(f"Duplicate key {key} in alias map")
    LOADED_TYPE_ALIASES[key] = cls


@lru_cache()
def get_base_class(cls: Type["PolymorphicModel"]) -> Type["PolymorphicModel"]:
    for cls_ in cls.mro():
        if not issubclass(cls_, PolymorphicModel):
            continue
        config = cls_.__dict__.get("Config")
        if config is not None and config.__dict__.get("is_base_type", False):
            return cls_
    return PolymorphicModel


def get_classpath(cls: Type) -> str:
    return f"{cls.__module__}.{cls.__name__}"


TPM = TypeVar("TPM", bound="PolymorphicModel")

FingerprintPart = Union[None, int, str, float, bool, bytes, Tuple["FingerprintPart", ...]]


class PolymorphicModel(BaseModel):
    class Config(BaseModel.Config):
        type_alias: ClassVar[Optional[str]] = None
        is_base_type: ClassVar[bool] = False

    __config__: ClassVar[Config]

    @classmethod
    def __get_type__(cls):
        config = cls.__dict__.get("Config")
        if config is not None and config.__dict__.get("type_alias") is not None:
            return config.type_alias
        return cls.__get_classpath__()

    @classmethod
    def __get_classpath__(cls):
        return get_classpath(cls)

    type: str = Field("")

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls == PolymorphicModel:
            return
        typename = cls.__get_type__()
        cls.__fields__["type"].default = typename
        register_loaded_alias(get_base_class(cls), cls, typename)

    @classmethod
    def __subtypes__(cls):
        return Union[tuple(all_subclasses(cls))]

    @classmethod
    def validate(cls: Type[TPM], value: Any) -> TPM:
        if isinstance(value, dict) and "type" in value:
            typename = value.pop("type")
            key = (get_base_class(cls), typename)  # type: ignore[arg-type]
            if key in LOADED_TYPE_ALIASES:
                subcls = LOADED_TYPE_ALIASES[key]
            else:
                if key in TYPE_ALIASES:
                    classpath = TYPE_ALIASES[key]
                else:
                    classpath = typename
                if not any(classpath.startswith(p) for p in ALLOWED_TYPE_PREFIXES):
                    raise ValueError(f"{classpath} does not match any allowed prefixes")
                subcls = import_string(classpath)
            return subcls.validate(value)
        return super().validate(value)  # type: ignore[misc]


def get_value_fingerprint(value: Any) -> FingerprintPart:
    if isinstance(value, EvidentlyBaseModel):
        return value.get_fingerprint()
    if isinstance(value, BaseModel):
        return get_value_fingerprint(value.dict())
    if dataclasses.is_dataclass(value):
        return get_value_fingerprint(dataclasses.asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    if isinstance(value, dict):
        return tuple((get_value_fingerprint(k), get_value_fingerprint(v)) for k, v in sorted(value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(get_value_fingerprint(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return tuple(get_value_fingerprint(v) for v in sorted(value, key=str))
    raise NotImplementedError(
        f"Not implemented for value of type {value.__class__.__module__}.{value.__class__.__name__}"
    )


class EvidentlyBaseModel(FrozenBaseModel, PolymorphicModel):
    def get_fingerprint(self) -> str:
        return hashlib.md5((self.__get_classpath__() + str(self.get_fingerprint_parts())).encode("utf8")).hexdigest()

    def get_fingerprint_parts(self) -> Tuple[FingerprintPart, ...]:
        return tuple(
            (name, self.get_field_fingerprint(name))
            for name, field in sorted(self.__fields__.items())
            if field.required or getattr(self, name) != field.get_default()
        )

    def get_field_fingerprint(self, field: str) -> FingerprintPart:
        value = getattr(self, field)
        return get_value_fingerprint(value)


class WithTestAndMetricDependencies(EvidentlyBaseModel):
    def __evidently_dependencies__(self):
        from evidently.base_metric import Metric
        from evidently.tests.base_test import Test

        for field_name, field in itertools.chain(
            self.__dict__.items(), ((pa, getattr(self, pa, None)) for pa in self.__private_attributes__)
        ):
            if issubclass(type(field), (Metric, Test)):
                yield field_name, field


class EnumValueMixin(BaseModel):
    def _to_enum_value(self, key, value):
        field = self.__fields__[key]
        if isinstance(field.type_, type) and not issubclass(field.type_, Enum):
            return value

        if isinstance(value, list):
            return [v.value if isinstance(v, Enum) else v for v in value]

        if isinstance(value, frozenset):
            return frozenset(v.value if isinstance(v, Enum) else v for v in value)

        if isinstance(value, set):
            return {v.value if isinstance(v, Enum) else v for v in value}
        return value.value if isinstance(value, Enum) else value

    def dict(self, *args, **kwargs) -> "DictStrAny":
        res = super().dict(*args, **kwargs)
        return {k: self._to_enum_value(k, v) for k, v in res.items()}


class ExcludeNoneMixin(BaseModel):
    def dict(self, *args, **kwargs) -> "DictStrAny":
        kwargs["exclude_none"] = True
        return super().dict(*args, **kwargs)


class FieldTags(Enum):
    Parameter = "parameter"
    Current = "current"
    Reference = "reference"
    Render = "render"
    TypeField = "type_field"
    Extra = "extra"


IncludeTags = FieldTags  # fixme: tmp for compatibility, remove in separate PR


class FieldInfo(EnumValueMixin):
    class Config:
        frozen = True

    path: str
    tags: FrozenSet[FieldTags]
    classpath: str

    def __lt__(self, other):
        return self.path < other.path


def _to_path(path: List[Any]) -> str:
    return ".".join(str(p) for p in path)


class FieldPath:
    def __init__(self, path: List[Any], cls_or_instance: Union[Type, Any], is_mapping: bool = False):
        self._path = path
        self._cls: Type
        self._instance: Any
        if is_union_type(cls_or_instance):
            cls_or_instance = get_args(cls_or_instance)[0]
        if isinstance(cls_or_instance, type):
            self._cls = cls_or_instance
            self._instance = None
        else:
            self._cls = type(cls_or_instance)
            self._instance = cls_or_instance
        self._is_mapping = is_mapping

    @property
    def has_instance(self):
        return self._instance is not None

    def list_fields(self) -> List[str]:
        if self.has_instance and self._is_mapping and isinstance(self._instance, dict):
            return list(self._instance.keys())
        if isinstance(self._cls, type) and issubclass(self._cls, BaseModel):
            return list(self._cls.__fields__)
        return []

    def __getattr__(self, item) -> "FieldPath":
        return self.child(item)

    def child(self, item: str) -> "FieldPath":
        if self._is_mapping:
            if self.has_instance and isinstance(self._instance, dict):
                return FieldPath(self._path + [item], self._instance[item])
            return FieldPath(self._path + [item], self._cls)
        if not issubclass(self._cls, BaseModel):
            raise AttributeError(f"{self._cls} does not have fields")
        if item not in self._cls.__fields__:
            raise AttributeError(f"{self._cls} type does not have '{item}' field")
        field = self._cls.__fields__[item]
        field_value = field.type_
        is_mapping = field.shape == SHAPE_DICT
        if self.has_instance:
            field_value = getattr(self._instance, item)
            if is_mapping:
                return FieldPath(self._path + [item], field_value, is_mapping=True)
        return FieldPath(self._path + [item], field_value, is_mapping=is_mapping)

    def list_nested_fields(self, exclude: Set["IncludeTags"] = None) -> List[str]:
        if not isinstance(self._cls, type) or not issubclass(self._cls, BaseModel):
            return [repr(self)]
        res = []
        for name, field in self._cls.__fields__.items():
            field_value = field.type_
            # todo: do something with recursive imports
            from evidently.core import get_field_tags

            field_tags = get_field_tags(self._cls, name)
            if field_tags is not None and (exclude is not None and any(t in exclude for t in field_tags)):
                continue
            is_mapping = field.shape == SHAPE_DICT
            if self.has_instance:
                field_value = getattr(self._instance, name)
                if is_mapping and isinstance(field_value, dict):
                    for key, value in field_value.items():
                        res.extend(FieldPath(self._path + [name, str(key)], value).list_nested_fields(exclude=exclude))
                    continue
            else:
                if is_mapping:
                    name = f"{name}.*"
            res.extend(FieldPath(self._path + [name], field_value).list_nested_fields(exclude=exclude))
        return res

    def _list_with_tags(self, current_tags: Set["IncludeTags"]) -> List[Tuple[List[Any], Set["IncludeTags"]]]:
        if not isinstance(self._cls, type) or not issubclass(self._cls, BaseModel):
            return [(self._path, current_tags)]
        from evidently.core import BaseResult

        if issubclass(self._cls, BaseResult) and self._cls.__config__.extract_as_obj:
            return [(self._path, current_tags)]
        res = []
        for name, field in self._cls.__fields__.items():
            field_value = field.type_

            # todo: do something with recursive imports
            from evidently.core import get_field_tags

            field_tags = get_field_tags(self._cls, name)

            is_mapping = field.shape == SHAPE_DICT
            if self.has_instance:
                field_value = getattr(self._instance, name)
                if is_mapping and isinstance(field_value, dict):
                    for key, value in field_value.items():
                        res.extend(
                            FieldPath(self._path + [name, key], value)._list_with_tags(current_tags.union(field_tags))
                        )
                    continue
            else:
                if is_mapping:
                    name = f"{name}.*"
            res.extend(FieldPath(self._path + [name], field_value)._list_with_tags(current_tags.union(field_tags)))
        return res

    def list_nested_fields_with_tags(self) -> List[Tuple[str, Set["IncludeTags"]]]:
        return [(_to_path(path), tags) for path, tags in self._list_with_tags(set())]

    def list_nested_field_infos(self) -> List[FieldInfo]:
        return [
            FieldInfo(path=_to_path(path), tags=frozenset(tags), classpath=get_classpath(self._get_field_type(path)))
            for path, tags in self._list_with_tags(set())
        ]

    def _get_field_type(self, path: List[str]) -> Type:
        if len(path) == 0:
            raise ValueError("Empty path provided")
        if len(path) == 1:
            if isinstance(self._cls, type) and issubclass(self._cls, BaseModel):
                return self._cls.__fields__[path[0]].type_
            if self.has_instance:
                # fixme: tmp fix
                # in case of field like f: Dict[str, A] we wont know that value was type annotated with A when we get to it
                if isinstance(self._instance, dict):
                    return type(self._instance.get(path[0]))
            raise NotImplementedError(f"Not implemented for {self._cls.__name__}")
        child, *path = path
        return self.child(child)._get_field_type(path)

    def __repr__(self):
        return self.get_path()

    def get_path(self):
        return ".".join(self._path)

    def __dir__(self) -> Iterable[str]:
        res: List[str] = []
        res.extend(super().__dir__())
        res.extend(self.list_fields())
        return res

    def get_field_tags(self, path: List[str]) -> Optional[Set["IncludeTags"]]:
        from evidently.base_metric import BaseResult

        if not isinstance(self._cls, type) or not issubclass(self._cls, BaseResult):
            return None
        self_tags = self._cls.__config__.tags
        if len(path) == 0:
            return self_tags
        field_name, *path = path
        # todo: do something with recursive imports
        from evidently.core import get_field_tags

        field_tags = get_field_tags(self._cls, field_name)
        return self_tags.union(field_tags).union(self.child(field_name).get_field_tags(path) or tuple())


@pydantic_type_validator(FieldPath)
def series_validator(value):
    return value.get_path()


def get_object_hash_deprecated(obj: Union[BaseModel, dict]):
    from evidently.utils import NumpyEncoder

    if isinstance(obj, BaseModel):
        obj = obj.dict()
    return hashlib.md5(json.dumps(obj, cls=NumpyEncoder).encode("utf8")).hexdigest()  # nosec: B324

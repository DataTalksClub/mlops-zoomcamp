from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from collections import Counter, abc, deque
from contextlib import suppress
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import EnumMeta
from functools import partial
from importlib import import_module
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
    ip_address,
    ip_interface,
    ip_network,
)
from os.path import realpath
from pathlib import Path
from random import Random
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Collection,
    Generic,
    Hashable,
    Iterable,
    Mapping,
    Sequence,
    Type,
    TypedDict,
    TypeVar,
    cast,
)
from uuid import UUID

from faker import Faker
from typing_extensions import get_args, get_origin, get_original_bases

from polyfactory.constants import (
    DEFAULT_RANDOM,
    MAX_COLLECTION_LENGTH,
    MIN_COLLECTION_LENGTH,
    RANDOMIZE_COLLECTION_LENGTH,
)
from polyfactory.exceptions import ConfigurationException, MissingBuildKwargException, ParameterException
from polyfactory.field_meta import Null
from polyfactory.fields import Fixture, Ignore, PostGenerated, Require, Use
from polyfactory.utils.helpers import (
    flatten_annotation,
    get_collection_type,
    unwrap_annotation,
    unwrap_args,
    unwrap_optional,
)
from polyfactory.utils.model_coverage import CoverageContainer, CoverageContainerCallable, resolve_kwargs_coverage
from polyfactory.utils.predicates import get_type_origin, is_any, is_literal, is_optional, is_safe_subclass, is_union
from polyfactory.utils.types import NoneType
from polyfactory.value_generators.complex_types import handle_collection_type, handle_collection_type_coverage
from polyfactory.value_generators.constrained_collections import (
    handle_constrained_collection,
    handle_constrained_mapping,
)
from polyfactory.value_generators.constrained_dates import handle_constrained_date
from polyfactory.value_generators.constrained_numbers import (
    handle_constrained_decimal,
    handle_constrained_float,
    handle_constrained_int,
)
from polyfactory.value_generators.constrained_path import handle_constrained_path
from polyfactory.value_generators.constrained_strings import handle_constrained_string_or_bytes
from polyfactory.value_generators.constrained_url import handle_constrained_url
from polyfactory.value_generators.constrained_uuid import handle_constrained_uuid
from polyfactory.value_generators.primitives import create_random_boolean, create_random_bytes, create_random_string

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

    from polyfactory.field_meta import Constraints, FieldMeta
    from polyfactory.persistence import AsyncPersistenceProtocol, SyncPersistenceProtocol


T = TypeVar("T")
F = TypeVar("F", bound="BaseFactory[Any]")


class BuildContext(TypedDict):
    seen_models: set[type]


def _get_build_context(build_context: BuildContext | None) -> BuildContext:
    if build_context is None:
        return {"seen_models": set()}

    return copy.deepcopy(build_context)


class BaseFactory(ABC, Generic[T]):
    """Base Factory class - this class holds the main logic of the library"""

    # configuration attributes
    __model__: type[T]
    """
    The model for the factory.
    This attribute is required for non-base factories and an exception will be raised if it's not set. Can be automatically inferred from the factory generic argument.
    """
    __check_model__: bool = False
    """
    Flag dictating whether to check if fields defined on the factory exists on the model or not.
    If 'True', checks will be done against Use, PostGenerated, Ignore, Require constructs fields only.
    """
    __allow_none_optionals__: ClassVar[bool] = True
    """
    Flag dictating whether to allow 'None' for optional values.
    If 'True', 'None' will be randomly generated as a value for optional model fields
    """
    __sync_persistence__: type[SyncPersistenceProtocol[T]] | SyncPersistenceProtocol[T] | None = None
    """A sync persistence handler. Can be a class or a class instance."""
    __async_persistence__: type[AsyncPersistenceProtocol[T]] | AsyncPersistenceProtocol[T] | None = None
    """An async persistence handler. Can be a class or a class instance."""
    __set_as_default_factory_for_type__ = False
    """
    Flag dictating whether to set as the default factory for the given type.
    If 'True' the factory will be used instead of dynamically generating a factory for the type.
    """
    __is_base_factory__: bool = False
    """
    Flag dictating whether the factory is a 'base' factory. Base factories are registered globally as handlers for types.
    For example, the 'DataclassFactory', 'TypedDictFactory' and 'ModelFactory' are all base factories.
    """
    __base_factory_overrides__: dict[Any, type[BaseFactory[Any]]] | None = None
    """
    A base factory to override with this factory. If this value is set, the given factory will replace the given base factory.

    Note: this value can only be set when '__is_base_factory__' is 'True'.
    """
    __faker__: ClassVar["Faker"] = Faker()
    """
    A faker instance to use. Can be a user provided value.
    """
    __random__: ClassVar["Random"] = DEFAULT_RANDOM
    """
    An instance of 'random.Random' to use.
    """
    __random_seed__: ClassVar[int]
    """
    An integer to seed the factory's Faker and Random instances with.
    This attribute can be used to control random generation.
    """
    __randomize_collection_length__: ClassVar[bool] = RANDOMIZE_COLLECTION_LENGTH
    """
    Flag dictating whether to randomize collections lengths.
    """
    __min_collection_length__: ClassVar[int] = MIN_COLLECTION_LENGTH
    """
    An integer value that defines minimum length of a collection.
    """
    __max_collection_length__: ClassVar[int] = MAX_COLLECTION_LENGTH
    """
    An integer value that defines maximum length of a collection.
    """
    __use_defaults__: ClassVar[bool] = False
    """
    Flag indicating whether to use the default value on a specific field, if provided.
    """

    __config_keys__: tuple[str, ...] = (
        "__check_model__",
        "__allow_none_optionals__",
        "__set_as_default_factory_for_type__",
        "__faker__",
        "__random__",
        "__randomize_collection_length__",
        "__min_collection_length__",
        "__max_collection_length__",
        "__use_defaults__",
    )
    """Keys to be considered as config values to pass on to dynamically created factories."""

    # cached attributes
    _fields_metadata: list[FieldMeta]
    # BaseFactory only attributes
    _factory_type_mapping: ClassVar[dict[Any, type[BaseFactory[Any]]]]
    _base_factories: ClassVar[list[type[BaseFactory[Any]]]]

    # Non-public attributes
    _extra_providers: dict[Any, Callable[[], Any]] | None = None

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:  # noqa: C901
        super().__init_subclass__(*args, **kwargs)

        if not hasattr(BaseFactory, "_base_factories"):
            BaseFactory._base_factories = []

        if not hasattr(BaseFactory, "_factory_type_mapping"):
            BaseFactory._factory_type_mapping = {}

        if cls.__min_collection_length__ > cls.__max_collection_length__:
            msg = "Minimum collection length shouldn't be greater than maximum collection length"
            raise ConfigurationException(
                msg,
            )

        if "__is_base_factory__" not in cls.__dict__ or not cls.__is_base_factory__:
            model: type[T] | None = getattr(cls, "__model__", None) or cls._infer_model_type()
            if not model:
                msg = f"required configuration attribute '__model__' is not set on {cls.__name__}"
                raise ConfigurationException(
                    msg,
                )
            cls.__model__ = model
            if not cls.is_supported_type(model):
                for factory in BaseFactory._base_factories:
                    if factory.is_supported_type(model):
                        msg = f"{cls.__name__} does not support {model.__name__}, but this type is supported by the {factory.__name__} base factory class. To resolve this error, subclass the factory from {factory.__name__} instead of {cls.__name__}"
                        raise ConfigurationException(
                            msg,
                        )
                    msg = f"Model type {model.__name__} is not supported. To support it, register an appropriate base factory and subclass it for your factory."
                    raise ConfigurationException(
                        msg,
                    )
            if cls.__check_model__:
                cls._check_declared_fields_exist_in_model()
        else:
            BaseFactory._base_factories.append(cls)

        random_seed = getattr(cls, "__random_seed__", None)
        if random_seed is not None:
            cls.seed_random(random_seed)

        if cls.__set_as_default_factory_for_type__ and hasattr(cls, "__model__"):
            BaseFactory._factory_type_mapping[cls.__model__] = cls

    @classmethod
    def _infer_model_type(cls: type[F]) -> type[T] | None:
        """Return model type inferred from class declaration.
        class Foo(ModelFactory[MyModel]):  # <<< MyModel
            ...

        If more than one base class and/or generic arguments specified return None.

        :returns: Inferred model type or None
        """

        factory_bases: Iterable[type[BaseFactory[T]]] = (
            b for b in get_original_bases(cls) if get_origin(b) and issubclass(get_origin(b), BaseFactory)
        )
        generic_args: Sequence[type[T]] = [
            arg for factory_base in factory_bases for arg in get_args(factory_base) if not isinstance(arg, TypeVar)
        ]
        if len(generic_args) != 1:
            return None

        return generic_args[0]

    @classmethod
    def _get_sync_persistence(cls) -> SyncPersistenceProtocol[T]:
        """Return a SyncPersistenceHandler if defined for the factory, otherwise raises a ConfigurationException.

        :raises: ConfigurationException
        :returns: SyncPersistenceHandler
        """
        if cls.__sync_persistence__:
            return cls.__sync_persistence__() if callable(cls.__sync_persistence__) else cls.__sync_persistence__
        msg = "A '__sync_persistence__' handler must be defined in the factory to use this method"
        raise ConfigurationException(
            msg,
        )

    @classmethod
    def _get_async_persistence(cls) -> AsyncPersistenceProtocol[T]:
        """Return a AsyncPersistenceHandler if defined for the factory, otherwise raises a ConfigurationException.

        :raises: ConfigurationException
        :returns: AsyncPersistenceHandler
        """
        if cls.__async_persistence__:
            return cls.__async_persistence__() if callable(cls.__async_persistence__) else cls.__async_persistence__
        msg = "An '__async_persistence__' handler must be defined in the factory to use this method"
        raise ConfigurationException(
            msg,
        )

    @classmethod
    def _handle_factory_field(  # noqa: PLR0911
        cls,
        field_value: Any,
        build_context: BuildContext,
        field_build_parameters: Any | None = None,
    ) -> Any:
        """Handle a value defined on the factory class itself.

        :param field_value: A value defined as an attribute on the factory class.
        :param field_build_parameters: Any build parameters passed to the factory as kwarg values.

        :returns: An arbitrary value correlating with the given field_meta value.
        """
        if is_safe_subclass(field_value, BaseFactory):
            if isinstance(field_build_parameters, Mapping):
                return field_value.build(_build_context=build_context, **field_build_parameters)

            if isinstance(field_build_parameters, Sequence):
                return [
                    field_value.build(_build_context=build_context, **parameter) for parameter in field_build_parameters
                ]

            return field_value.build(_build_context=build_context)

        if isinstance(field_value, Use):
            return field_value.to_value()

        if isinstance(field_value, Fixture):
            return field_value.to_value()

        if callable(field_value):
            return field_value()

        return field_value if isinstance(field_value, Hashable) else copy.deepcopy(field_value)

    @classmethod
    def _handle_factory_field_coverage(
        cls,
        field_value: Any,
        field_build_parameters: Any | None = None,
        build_context: BuildContext | None = None,
    ) -> Any:
        """Handle a value defined on the factory class itself.

        :param field_value: A value defined as an attribute on the factory class.
        :param field_build_parameters: Any build parameters passed to the factory as kwarg values.

        :returns: An arbitrary value correlating with the given field_meta value.
        """
        if is_safe_subclass(field_value, BaseFactory):
            if isinstance(field_build_parameters, Mapping):
                return CoverageContainer(field_value.coverage(_build_context=build_context, **field_build_parameters))

            if isinstance(field_build_parameters, Sequence):
                return [
                    CoverageContainer(field_value.coverage(_build_context=build_context, **parameter))
                    for parameter in field_build_parameters
                ]

            return CoverageContainer(field_value.coverage())

        if isinstance(field_value, Use):
            return field_value.to_value()

        if isinstance(field_value, Fixture):
            return CoverageContainerCallable(field_value.to_value)

        return CoverageContainerCallable(field_value) if callable(field_value) else field_value

    @classmethod
    def _get_config(cls) -> dict[str, Any]:
        return {
            **{key: getattr(cls, key) for key in cls.__config_keys__},
            "_extra_providers": cls.get_provider_map(),
        }

    @classmethod
    def _get_or_create_factory(cls, model: type) -> type[BaseFactory[Any]]:
        """Get a factory from registered factories or generate a factory dynamically.

        :param model: A model type.
        :returns: A Factory sub-class.

        """
        if factory := BaseFactory._factory_type_mapping.get(model):
            return factory

        config = cls._get_config()

        if cls.__base_factory_overrides__:
            for model_ancestor in model.mro():
                if factory := cls.__base_factory_overrides__.get(model_ancestor):
                    return factory.create_factory(model, **config)

        for factory in reversed(BaseFactory._base_factories):
            if factory.is_supported_type(model):
                return factory.create_factory(model, **config)

        msg = f"unsupported model type {model.__name__}"
        raise ParameterException(msg)  # pragma: no cover

    # Public Methods

    @classmethod
    def is_factory_type(cls, annotation: Any) -> bool:
        """Determine whether a given field is annotated with a type that is supported by a base factory.

        :param annotation: A type annotation.
        :returns: Boolean dictating whether the annotation is a factory type
        """
        return any(factory.is_supported_type(annotation) for factory in BaseFactory._base_factories)

    @classmethod
    def is_batch_factory_type(cls, annotation: Any) -> bool:
        """Determine whether a given field is annotated with a sequence of supported factory types.

        :param annotation: A type annotation.
        :returns: Boolean dictating whether the annotation is a batch factory type
        """
        origin = get_type_origin(annotation) or annotation
        if is_safe_subclass(origin, Sequence) and (args := unwrap_args(annotation, random=cls.__random__)):
            return len(args) == 1 and BaseFactory.is_factory_type(annotation=args[0])
        return False

    @classmethod
    def extract_field_build_parameters(cls, field_meta: FieldMeta, build_args: dict[str, Any]) -> Any:
        """Extract from the build kwargs any build parameters passed for a given field meta - if it is a factory type.

        :param field_meta: A field meta instance.
        :param build_args: Any kwargs passed to the factory.
        :returns: Any values
        """
        if build_arg := build_args.get(field_meta.name):
            annotation = unwrap_optional(field_meta.annotation)
            if (
                BaseFactory.is_factory_type(annotation=annotation)
                and isinstance(build_arg, Mapping)
                and not BaseFactory.is_factory_type(annotation=type(build_arg))
            ):
                return build_args.pop(field_meta.name)

            if (
                BaseFactory.is_batch_factory_type(annotation=annotation)
                and isinstance(build_arg, Sequence)
                and not any(BaseFactory.is_factory_type(annotation=type(value)) for value in build_arg)
            ):
                return build_args.pop(field_meta.name)
        return None

    @classmethod
    @abstractmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[type[T]]":  # pragma: no cover
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        raise NotImplementedError

    @classmethod
    def seed_random(cls, seed: int) -> None:
        """Seed faker and random with the given integer.

        :param seed: An integer to set as seed.
        :returns: 'None'

        """
        cls.__random__ = Random(seed)
        cls.__faker__.seed_instance(seed)

    @classmethod
    def is_ignored_type(cls, value: Any) -> bool:
        """Check whether a given value is an ignored type.

        :param value: An arbitrary value.

        :notes:
            - This method is meant to be overwritten by extension factories and other subclasses

        :returns: A boolean determining whether the value should be ignored.

        """
        return value is None

    @classmethod
    def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
        """Map types to callables.

        :notes:
            - This method is distinct to allow overriding.


        :returns: a dictionary mapping types to callables.

        """

        def _create_generic_fn() -> Callable:
            """Return a generic lambda"""
            return lambda *args: None

        return {
            Any: lambda: None,
            # primitives
            object: object,
            float: cls.__faker__.pyfloat,
            int: cls.__faker__.pyint,
            bool: cls.__faker__.pybool,
            str: cls.__faker__.pystr,
            bytes: partial(create_random_bytes, cls.__random__),
            # built-in objects
            dict: cls.__faker__.pydict,
            tuple: cls.__faker__.pytuple,
            list: cls.__faker__.pylist,
            set: cls.__faker__.pyset,
            frozenset: lambda: frozenset(cls.__faker__.pylist()),
            deque: lambda: deque(cls.__faker__.pylist()),
            # standard library objects
            Path: lambda: Path(realpath(__file__)),
            Decimal: cls.__faker__.pydecimal,
            UUID: lambda: UUID(str(cls.__faker__.uuid4())),
            # datetime
            datetime: cls.__faker__.date_time_between,
            date: cls.__faker__.date_this_decade,
            time: cls.__faker__.time_object,
            timedelta: cls.__faker__.time_delta,
            # ip addresses
            IPv4Address: lambda: ip_address(cls.__faker__.ipv4()),
            IPv4Interface: lambda: ip_interface(cls.__faker__.ipv4()),
            IPv4Network: lambda: ip_network(cls.__faker__.ipv4(network=True)),
            IPv6Address: lambda: ip_address(cls.__faker__.ipv6()),
            IPv6Interface: lambda: ip_interface(cls.__faker__.ipv6()),
            IPv6Network: lambda: ip_network(cls.__faker__.ipv6(network=True)),
            # types
            Callable: _create_generic_fn,
            abc.Callable: _create_generic_fn,
            Counter: lambda: Counter(cls.__faker__.pystr()),
            **(cls._extra_providers or {}),
        }

    @classmethod
    def create_factory(
        cls: type[F],
        model: type[T] | None = None,
        bases: tuple[type[BaseFactory[Any]], ...] | None = None,
        **kwargs: Any,
    ) -> type[F]:
        """Generate a factory for the given type dynamically.

        :param model: A type to model. Defaults to current factory __model__ if any.
            Otherwise, raise an error
        :param bases: Base classes to use when generating the new class.
        :param kwargs: Any kwargs.

        :returns: A 'ModelFactory' subclass.

        """
        if model is None:
            try:
                model = cls.__model__
            except AttributeError as ex:
                msg = "A 'model' argument is required when creating a new factory from a base one"
                raise TypeError(msg) from ex
        return cast(
            "Type[F]",
            type(
                f"{model.__name__}Factory",  # pyright: ignore[reportOptionalMemberAccess]
                (*(bases or ()), cls),
                {"__model__": model, **kwargs},
            ),
        )

    @classmethod
    def get_constrained_field_value(cls, annotation: Any, field_meta: FieldMeta) -> Any:  # noqa: C901, PLR0911, PLR0912
        try:
            constraints = cast("Constraints", field_meta.constraints)
            if is_safe_subclass(annotation, float):
                return handle_constrained_float(
                    random=cls.__random__,
                    multiple_of=cast("Any", constraints.get("multiple_of")),
                    gt=cast("Any", constraints.get("gt")),
                    ge=cast("Any", constraints.get("ge")),
                    lt=cast("Any", constraints.get("lt")),
                    le=cast("Any", constraints.get("le")),
                )

            if is_safe_subclass(annotation, int):
                return handle_constrained_int(
                    random=cls.__random__,
                    multiple_of=cast("Any", constraints.get("multiple_of")),
                    gt=cast("Any", constraints.get("gt")),
                    ge=cast("Any", constraints.get("ge")),
                    lt=cast("Any", constraints.get("lt")),
                    le=cast("Any", constraints.get("le")),
                )

            if is_safe_subclass(annotation, Decimal):
                return handle_constrained_decimal(
                    random=cls.__random__,
                    decimal_places=cast("Any", constraints.get("decimal_places")),
                    max_digits=cast("Any", constraints.get("max_digits")),
                    multiple_of=cast("Any", constraints.get("multiple_of")),
                    gt=cast("Any", constraints.get("gt")),
                    ge=cast("Any", constraints.get("ge")),
                    lt=cast("Any", constraints.get("lt")),
                    le=cast("Any", constraints.get("le")),
                )

            if url_constraints := constraints.get("url"):
                return handle_constrained_url(constraints=url_constraints)

            if is_safe_subclass(annotation, str) or is_safe_subclass(annotation, bytes):
                return handle_constrained_string_or_bytes(
                    random=cls.__random__,
                    t_type=str if is_safe_subclass(annotation, str) else bytes,
                    lower_case=constraints.get("lower_case") or False,
                    upper_case=constraints.get("upper_case") or False,
                    min_length=constraints.get("min_length"),
                    max_length=constraints.get("max_length"),
                    pattern=constraints.get("pattern"),
                )

            try:
                collection_type = get_collection_type(annotation)
            except ValueError:
                collection_type = None
            if collection_type is not None:
                if collection_type == dict:
                    return handle_constrained_mapping(
                        factory=cls,
                        field_meta=field_meta,
                        min_items=constraints.get("min_length"),
                        max_items=constraints.get("max_length"),
                    )
                return handle_constrained_collection(
                    collection_type=collection_type,  # type: ignore[type-var]
                    factory=cls,
                    field_meta=field_meta.children[0] if field_meta.children else field_meta,
                    item_type=constraints.get("item_type"),
                    max_items=constraints.get("max_length"),
                    min_items=constraints.get("min_length"),
                    unique_items=constraints.get("unique_items", False),
                )

            if is_safe_subclass(annotation, date):
                return handle_constrained_date(
                    faker=cls.__faker__,
                    ge=cast("Any", constraints.get("ge")),
                    gt=cast("Any", constraints.get("gt")),
                    le=cast("Any", constraints.get("le")),
                    lt=cast("Any", constraints.get("lt")),
                    tz=cast("Any", constraints.get("tz")),
                )

            if is_safe_subclass(annotation, UUID) and (uuid_version := constraints.get("uuid_version")):
                return handle_constrained_uuid(
                    uuid_version=uuid_version,
                    faker=cls.__faker__,
                )

            if is_safe_subclass(annotation, Path) and (path_constraint := constraints.get("path_type")):
                return handle_constrained_path(constraint=path_constraint, faker=cls.__faker__)
        except TypeError as e:
            raise ParameterException from e

        msg = f"received constraints for unsupported type {annotation}"
        raise ParameterException(msg)

    @classmethod
    def get_field_value(  # noqa: C901, PLR0911, PLR0912
        cls,
        field_meta: FieldMeta,
        field_build_parameters: Any | None = None,
        build_context: BuildContext | None = None,
    ) -> Any:
        """Return a field value on the subclass if existing, otherwise returns a mock value.

        :param field_meta: FieldMeta instance.
        :param field_build_parameters: Any build parameters passed to the factory as kwarg values.
        :param build_context: BuildContext data for current build.

        :returns: An arbitrary value.

        """
        build_context = _get_build_context(build_context)
        if cls.is_ignored_type(field_meta.annotation):
            return None

        if field_build_parameters is None and cls.should_set_none_value(field_meta=field_meta):
            return None

        unwrapped_annotation = unwrap_annotation(field_meta.annotation, random=cls.__random__)

        if is_literal(annotation=unwrapped_annotation) and (literal_args := get_args(unwrapped_annotation)):
            return cls.__random__.choice(literal_args)

        if isinstance(unwrapped_annotation, EnumMeta):
            return cls.__random__.choice(list(unwrapped_annotation))

        if field_meta.constraints:
            return cls.get_constrained_field_value(annotation=unwrapped_annotation, field_meta=field_meta)

        if is_union(field_meta.annotation) and field_meta.children:
            seen_models = build_context["seen_models"]
            children = [child for child in field_meta.children if child.annotation not in seen_models]

            # `None` is removed from the children when creating FieldMeta so when `children`
            # is empty, it must mean that the field meta is an optional type.
            if children:
                return cls.get_field_value(cls.__random__.choice(children), field_build_parameters, build_context)

        if BaseFactory.is_factory_type(annotation=unwrapped_annotation):
            if not field_build_parameters and unwrapped_annotation in build_context["seen_models"]:
                return None if is_optional(field_meta.annotation) else Null

            return cls._get_or_create_factory(model=unwrapped_annotation).build(
                _build_context=build_context,
                **(field_build_parameters if isinstance(field_build_parameters, Mapping) else {}),
            )

        if BaseFactory.is_batch_factory_type(annotation=unwrapped_annotation):
            factory = cls._get_or_create_factory(model=field_meta.type_args[0])
            if isinstance(field_build_parameters, Sequence):
                return [
                    factory.build(_build_context=build_context, **field_parameters)
                    for field_parameters in field_build_parameters
                ]

            if field_meta.type_args[0] in build_context["seen_models"]:
                return []

            if not cls.__randomize_collection_length__:
                return [factory.build(_build_context=build_context)]

            batch_size = cls.__random__.randint(cls.__min_collection_length__, cls.__max_collection_length__)
            return factory.batch(size=batch_size, _build_context=build_context)

        if (origin := get_type_origin(unwrapped_annotation)) and is_safe_subclass(origin, Collection):
            if cls.__randomize_collection_length__:
                collection_type = get_collection_type(unwrapped_annotation)
                if collection_type != dict:
                    return handle_constrained_collection(
                        collection_type=collection_type,  # type: ignore[type-var]
                        factory=cls,
                        item_type=Any,
                        field_meta=field_meta.children[0] if field_meta.children else field_meta,
                        min_items=cls.__min_collection_length__,
                        max_items=cls.__max_collection_length__,
                    )
                return handle_constrained_mapping(
                    factory=cls,
                    field_meta=field_meta,
                    min_items=cls.__min_collection_length__,
                    max_items=cls.__max_collection_length__,
                )

            return handle_collection_type(field_meta, origin, cls)

        if is_any(unwrapped_annotation) or isinstance(unwrapped_annotation, TypeVar):
            return create_random_string(cls.__random__, min_length=1, max_length=10)

        if provider := cls.get_provider_map().get(unwrapped_annotation):
            return provider()

        if callable(unwrapped_annotation):
            # if value is a callable we can try to naively call it.
            # this will work for callables that do not require any parameters passed
            with suppress(Exception):
                return unwrapped_annotation()

        msg = f"Unsupported type: {unwrapped_annotation!r}\n\nEither extend the providers map or add a factory function for this type."
        raise ParameterException(
            msg,
        )

    @classmethod
    def get_field_value_coverage(  # noqa: C901
        cls,
        field_meta: FieldMeta,
        field_build_parameters: Any | None = None,
        build_context: BuildContext | None = None,
    ) -> Iterable[Any]:
        """Return a field value on the subclass if existing, otherwise returns a mock value.

        :param field_meta: FieldMeta instance.
        :param field_build_parameters: Any build parameters passed to the factory as kwarg values.
        :param build_context: BuildContext data for current build.

        :returns: An iterable of values.

        """
        if cls.is_ignored_type(field_meta.annotation):
            return

        for unwrapped_annotation in flatten_annotation(field_meta.annotation):
            if unwrapped_annotation in (None, NoneType):
                yield None

            elif is_literal(annotation=unwrapped_annotation) and (literal_args := get_args(unwrapped_annotation)):
                yield CoverageContainer(literal_args)

            elif isinstance(unwrapped_annotation, EnumMeta):
                yield CoverageContainer(list(unwrapped_annotation))

            elif field_meta.constraints:
                yield CoverageContainerCallable(
                    cls.get_constrained_field_value,
                    annotation=unwrapped_annotation,
                    field_meta=field_meta,
                )

            elif BaseFactory.is_factory_type(annotation=unwrapped_annotation):
                yield CoverageContainer(
                    cls._get_or_create_factory(model=unwrapped_annotation).coverage(
                        _build_context=build_context,
                        **(field_build_parameters if isinstance(field_build_parameters, Mapping) else {}),
                    ),
                )

            elif (origin := get_type_origin(unwrapped_annotation)) and issubclass(origin, Collection):
                yield handle_collection_type_coverage(field_meta, origin, cls)

            elif is_any(unwrapped_annotation) or isinstance(unwrapped_annotation, TypeVar):
                yield create_random_string(cls.__random__, min_length=1, max_length=10)

            elif provider := cls.get_provider_map().get(unwrapped_annotation):
                yield CoverageContainerCallable(provider)

            elif callable(unwrapped_annotation):
                # if value is a callable we can try to naively call it.
                # this will work for callables that do not require any parameters passed
                yield CoverageContainerCallable(unwrapped_annotation)
            else:
                msg = f"Unsupported type: {unwrapped_annotation!r}\n\nEither extend the providers map or add a factory function for this type."
                raise ParameterException(
                    msg,
                )

    @classmethod
    def should_set_none_value(cls, field_meta: FieldMeta) -> bool:
        """Determine whether a given model field_meta should be set to None.

        :param field_meta: Field metadata.

        :notes:
            - This method is distinct to allow overriding.

        :returns: A boolean determining whether 'None' should be set for the given field_meta.

        """
        return (
            cls.__allow_none_optionals__
            and is_optional(field_meta.annotation)
            and create_random_boolean(random=cls.__random__)
        )

    @classmethod
    def should_use_default_value(cls, field_meta: FieldMeta) -> bool:
        """Determine whether to use the default value for the given field.

        :param field_meta: FieldMeta instance.

        :notes:
            - This method is distinct to allow overriding.

        :returns: A boolean determining whether the default value should be used for the given field_meta.

        """
        return cls.__use_defaults__ and field_meta.default is not Null

    @classmethod
    def should_set_field_value(cls, field_meta: FieldMeta, **kwargs: Any) -> bool:
        """Determine whether to set a value for a given field_name.

        :param field_meta: FieldMeta instance.
        :param kwargs: Any kwargs passed to the factory.

        :notes:
            - This method is distinct to allow overriding.

        :returns: A boolean determining whether a value should be set for the given field_meta.

        """
        return not field_meta.name.startswith("_") and field_meta.name not in kwargs

    @classmethod
    @abstractmethod
    def get_model_fields(cls) -> list[FieldMeta]:  # pragma: no cover
        """Retrieve a list of fields from the factory's model.


        :returns: A list of field MetaData instances.

        """
        raise NotImplementedError

    @classmethod
    def get_factory_fields(cls) -> list[tuple[str, Any]]:
        """Retrieve a list of fields from the factory.

        Trying to be smart about what should be considered a field on the model,
        ignoring dunder methods and some parent class attributes.

        :returns: A list of tuples made of field name and field definition
        """
        factory_fields = cls.__dict__.items()
        return [
            (field_name, field_value)
            for field_name, field_value in factory_fields
            if not (field_name.startswith("__") or field_name == "_abc_impl")
        ]

    @classmethod
    def _check_declared_fields_exist_in_model(cls) -> None:
        model_fields_names = {field_meta.name for field_meta in cls.get_model_fields()}
        factory_fields = cls.get_factory_fields()

        for field_name, field_value in factory_fields:
            if field_name in model_fields_names:
                continue

            error_message = (
                f"{field_name} is declared on the factory {cls.__name__}"
                f" but it is not part of the model {cls.__model__.__name__}"
            )
            if isinstance(field_value, (Use, PostGenerated, Ignore, Require)):
                raise ConfigurationException(error_message)

    @classmethod
    def process_kwargs(cls, **kwargs: Any) -> dict[str, Any]:
        """Process the given kwargs and generate values for the factory's model.

        :param kwargs: Any build kwargs.

        :returns: A dictionary of build results.

        """
        _build_context = _get_build_context(kwargs.pop("_build_context", None))
        _build_context["seen_models"].add(cls.__model__)

        result: dict[str, Any] = {**kwargs}
        generate_post: dict[str, PostGenerated] = {}

        for field_meta in cls.get_model_fields():
            field_build_parameters = cls.extract_field_build_parameters(field_meta=field_meta, build_args=kwargs)
            if cls.should_set_field_value(field_meta, **kwargs) and not cls.should_use_default_value(field_meta):
                if hasattr(cls, field_meta.name) and not hasattr(BaseFactory, field_meta.name):
                    field_value = getattr(cls, field_meta.name)
                    if isinstance(field_value, Ignore):
                        continue

                    if isinstance(field_value, Require) and field_meta.name not in kwargs:
                        msg = f"Require kwarg {field_meta.name} is missing"
                        raise MissingBuildKwargException(msg)

                    if isinstance(field_value, PostGenerated):
                        generate_post[field_meta.name] = field_value
                        continue

                    result[field_meta.name] = cls._handle_factory_field(
                        field_value=field_value,
                        field_build_parameters=field_build_parameters,
                        build_context=_build_context,
                    )
                    continue

                field_result = cls.get_field_value(
                    field_meta,
                    field_build_parameters=field_build_parameters,
                    build_context=_build_context,
                )
                if field_result is Null:
                    continue

                result[field_meta.name] = field_result

        for field_name, post_generator in generate_post.items():
            result[field_name] = post_generator.to_value(field_name, result)

        return result

    @classmethod
    def process_kwargs_coverage(cls, **kwargs: Any) -> abc.Iterable[dict[str, Any]]:
        """Process the given kwargs and generate values for the factory's model.

        :param kwargs: Any build kwargs.
        :param build_context: BuildContext data for current build.

        :returns: A dictionary of build results.

        """
        _build_context = _get_build_context(kwargs.pop("_build_context", None))
        _build_context["seen_models"].add(cls.__model__)

        result: dict[str, Any] = {**kwargs}
        generate_post: dict[str, PostGenerated] = {}

        for field_meta in cls.get_model_fields():
            field_build_parameters = cls.extract_field_build_parameters(field_meta=field_meta, build_args=kwargs)

            if cls.should_set_field_value(field_meta, **kwargs):
                if hasattr(cls, field_meta.name) and not hasattr(BaseFactory, field_meta.name):
                    field_value = getattr(cls, field_meta.name)
                    if isinstance(field_value, Ignore):
                        continue

                    if isinstance(field_value, Require) and field_meta.name not in kwargs:
                        msg = f"Require kwarg {field_meta.name} is missing"
                        raise MissingBuildKwargException(msg)

                    if isinstance(field_value, PostGenerated):
                        generate_post[field_meta.name] = field_value
                        continue

                    result[field_meta.name] = cls._handle_factory_field_coverage(
                        field_value=field_value,
                        field_build_parameters=field_build_parameters,
                        build_context=_build_context,
                    )
                    continue

                result[field_meta.name] = CoverageContainer(
                    cls.get_field_value_coverage(
                        field_meta,
                        field_build_parameters=field_build_parameters,
                        build_context=_build_context,
                    ),
                )

        for resolved in resolve_kwargs_coverage(result):
            for field_name, post_generator in generate_post.items():
                resolved[field_name] = post_generator.to_value(field_name, resolved)
            yield resolved

    @classmethod
    def build(cls, **kwargs: Any) -> T:
        """Build an instance of the factory's __model__

        :param kwargs: Any kwargs. If field names are set in kwargs, their values will be used.

        :returns: An instance of type T.

        """
        return cast("T", cls.__model__(**cls.process_kwargs(**kwargs)))

    @classmethod
    def batch(cls, size: int, **kwargs: Any) -> list[T]:
        """Build a batch of size n of the factory's Meta.model.

        :param size: Size of the batch.
        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: A list of instances of type T.

        """
        return [cls.build(**kwargs) for _ in range(size)]

    @classmethod
    def coverage(cls, **kwargs: Any) -> abc.Iterator[T]:
        """Build a batch of the factory's Meta.model will full coverage of the sub-types of the model.

        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: A iterator of instances of type T.

        """
        for data in cls.process_kwargs_coverage(**kwargs):
            instance = cls.__model__(**data)
            yield cast("T", instance)

    @classmethod
    def create_sync(cls, **kwargs: Any) -> T:
        """Build and persists synchronously a single model instance.

        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: An instance of type T.

        """
        return cls._get_sync_persistence().save(data=cls.build(**kwargs))

    @classmethod
    def create_batch_sync(cls, size: int, **kwargs: Any) -> list[T]:
        """Build and persists synchronously a batch of n size model instances.

        :param size: Size of the batch.
        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: A list of instances of type T.

        """
        return cls._get_sync_persistence().save_many(data=cls.batch(size, **kwargs))

    @classmethod
    async def create_async(cls, **kwargs: Any) -> T:
        """Build and persists asynchronously a single model instance.

        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: An instance of type T.
        """
        return await cls._get_async_persistence().save(data=cls.build(**kwargs))

    @classmethod
    async def create_batch_async(cls, size: int, **kwargs: Any) -> list[T]:
        """Build and persists asynchronously a batch of n size model instances.


        :param size: Size of the batch.
        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: A list of instances of type T.
        """
        return await cls._get_async_persistence().save_many(data=cls.batch(size, **kwargs))


def _register_builtin_factories() -> None:
    """This function is used to register the base factories, if present.

    :returns: None
    """
    import polyfactory.factories.dataclass_factory
    import polyfactory.factories.typed_dict_factory  # noqa: F401

    for module in [
        "polyfactory.factories.pydantic_factory",
        "polyfactory.factories.beanie_odm_factory",
        "polyfactory.factories.odmantic_odm_factory",
        "polyfactory.factories.msgspec_factory",
        # `AttrsFactory` is not being registered by default since not all versions of `attrs` are supported.
        # Issue: https://github.com/litestar-org/polyfactory/issues/356
        # "polyfactory.factories.attrs_factory",
    ]:
        try:
            import_module(module)
        except ImportError:  # noqa: PERF203
            continue


_register_builtin_factories()

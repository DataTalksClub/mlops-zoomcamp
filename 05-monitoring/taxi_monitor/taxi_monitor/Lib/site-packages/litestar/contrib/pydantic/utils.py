# mypy: strict-equality=False
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from typing_extensions import Annotated, get_type_hints

from litestar.params import KwargDefinition
from litestar.types import Empty
from litestar.typing import FieldDefinition
from litestar.utils import deprecated, is_class_and_subclass
from litestar.utils.predicates import is_generic
from litestar.utils.typing import (
    _substitute_typevars,
    get_origin_or_inner_type,
    get_type_hints_with_generics_resolved,
    normalize_type_annotation,
)

# isort: off
try:
    from pydantic import v1 as pydantic_v1
    import pydantic as pydantic_v2
    from pydantic.fields import PydanticUndefined as Pydantic2Undefined  # type: ignore[attr-defined]
    from pydantic.v1.fields import Undefined as Pydantic1Undefined

    PYDANTIC_UNDEFINED_SENTINELS = {Pydantic1Undefined, Pydantic2Undefined}
except ImportError:
    try:
        import pydantic as pydantic_v1  # type: ignore[no-redef]
        from pydantic.fields import Undefined as Pydantic1Undefined  # type: ignore[attr-defined, no-redef]

        pydantic_v2 = Empty  # type: ignore[assignment]
        PYDANTIC_UNDEFINED_SENTINELS = {Pydantic1Undefined}

    except ImportError:  # pyright: ignore
        pydantic_v1 = Empty  # type: ignore[assignment]
        pydantic_v2 = Empty  # type: ignore[assignment]
        PYDANTIC_UNDEFINED_SENTINELS = set()
# isort: on


if TYPE_CHECKING:
    from types import ModuleType

    from typing_extensions import TypeGuard


def is_pydantic_model_class(
    annotation: Any,
) -> TypeGuard[type[pydantic_v1.BaseModel | pydantic_v2.BaseModel]]:  # pyright: ignore
    """Given a type annotation determine if the annotation is a subclass of pydantic's BaseModel.

    Args:
        annotation: A type.

    Returns:
        A typeguard determining whether the type is :data:`BaseModel pydantic.BaseModel>`.
    """
    tests: list[bool] = []

    if pydantic_v1 is not Empty:  # pragma: no cover
        tests.append(is_class_and_subclass(annotation, pydantic_v1.BaseModel))

    if pydantic_v2 is not Empty:  # pragma: no cover
        tests.append(is_class_and_subclass(annotation, pydantic_v2.BaseModel))

    return any(tests)


def is_pydantic_model_instance(
    annotation: Any,
) -> TypeGuard[pydantic_v1.BaseModel | pydantic_v2.BaseModel]:  # pyright: ignore
    """Given a type annotation determine if the annotation is an instance of pydantic's BaseModel.

    Args:
        annotation: A type.

    Returns:
        A typeguard determining whether the type is :data:`BaseModel pydantic.BaseModel>`.
    """
    tests: list[bool] = []

    if pydantic_v1 is not Empty:  # pragma: no cover
        tests.append(isinstance(annotation, pydantic_v1.BaseModel))

    if pydantic_v2 is not Empty:  # pragma: no cover
        tests.append(isinstance(annotation, pydantic_v2.BaseModel))

    return any(tests)


def is_pydantic_constrained_field(annotation: Any) -> bool:
    """Check if the given annotation is a constrained pydantic type.

    Args:
        annotation: A type annotation

    Returns:
        True if pydantic is installed and the type is a constrained type, otherwise False.
    """
    if pydantic_v1 is Empty:  # pragma: no cover
        return False  # type: ignore[unreachable]

    return any(
        is_class_and_subclass(annotation, constrained_type)  # pyright: ignore
        for constrained_type in (
            pydantic_v1.ConstrainedBytes,
            pydantic_v1.ConstrainedDate,
            pydantic_v1.ConstrainedDecimal,
            pydantic_v1.ConstrainedFloat,
            pydantic_v1.ConstrainedFrozenSet,
            pydantic_v1.ConstrainedInt,
            pydantic_v1.ConstrainedList,
            pydantic_v1.ConstrainedSet,
            pydantic_v1.ConstrainedStr,
        )
    )


def pydantic_unwrap_and_get_origin(annotation: Any) -> Any | None:
    if pydantic_v2 is Empty or (pydantic_v1 is not Empty and is_class_and_subclass(annotation, pydantic_v1.BaseModel)):
        return get_origin_or_inner_type(annotation)

    origin = annotation.__pydantic_generic_metadata__["origin"]
    return normalize_type_annotation(origin)


def pydantic_get_type_hints_with_generics_resolved(
    annotation: Any,
    globalns: dict[str, Any] | None = None,
    localns: dict[str, Any] | None = None,
    include_extras: bool = False,
    model_annotations: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if pydantic_v2 is Empty or (pydantic_v1 is not Empty and is_class_and_subclass(annotation, pydantic_v1.BaseModel)):
        return get_type_hints_with_generics_resolved(annotation, type_hints=model_annotations)

    origin = pydantic_unwrap_and_get_origin(annotation)
    if origin is None:
        if model_annotations is None:  # pragma: no cover
            model_annotations = get_type_hints(
                annotation, globalns=globalns, localns=localns, include_extras=include_extras
            )
        typevar_map = {p: p for p in annotation.__pydantic_generic_metadata__["parameters"]}
    else:
        if model_annotations is None:
            model_annotations = get_type_hints(
                origin, globalns=globalns, localns=localns, include_extras=include_extras
            )
        args = annotation.__pydantic_generic_metadata__["args"]
        parameters = origin.__pydantic_generic_metadata__["parameters"]
        typevar_map = dict(zip(parameters, args))

    return {n: _substitute_typevars(type_, typevar_map) for n, type_ in model_annotations.items()}


@deprecated(version="2.6.2")
def pydantic_get_unwrapped_annotation_and_type_hints(annotation: Any) -> tuple[Any, dict[str, Any]]:  # pragma:  pver
    """Get the unwrapped annotation and the type hints after resolving generics.

    Args:
        annotation: A type annotation.

    Returns:
        A tuple containing the unwrapped annotation and the type hints.
    """

    if is_generic(annotation):
        origin = pydantic_unwrap_and_get_origin(annotation)
        return origin or annotation, pydantic_get_type_hints_with_generics_resolved(annotation, include_extras=True)
    return annotation, get_type_hints(annotation, include_extras=True)


def is_pydantic_2_model(
    obj: type[pydantic_v1.BaseModel | pydantic_v2.BaseModel],  # pyright: ignore
) -> TypeGuard[pydantic_v2.BaseModel]:  # pyright: ignore
    return pydantic_v2 is not Empty and issubclass(obj, pydantic_v2.BaseModel)


def is_pydantic_undefined(value: Any) -> bool:
    return any(v is value for v in PYDANTIC_UNDEFINED_SENTINELS)


def create_field_definitions_for_computed_fields(
    model: type[pydantic_v1.BaseModel | pydantic_v2.BaseModel],  # pyright: ignore
    prefer_alias: bool,
) -> dict[str, FieldDefinition]:
    """Create field definitions for computed fields.

    Args:
        model: A pydantic model.
        prefer_alias: Whether to prefer the alias or the name of the field.

    Returns:
        A dictionary containing the field definitions for the computed fields.
    """
    pydantic_decorators = getattr(model, "__pydantic_decorators__", None)
    if pydantic_decorators is None:
        return {}

    def get_name(k: str, dec: Any) -> str:
        if not dec.info.alias:
            return k
        return dec.info.alias if prefer_alias else k  # type: ignore[no-any-return]

    return {
        (name := get_name(k, dec)): FieldDefinition.from_annotation(
            Annotated[
                dec.info.return_type,
                KwargDefinition(title=dec.info.title, description=dec.info.description, read_only=True),
            ],
            name=name,
        )
        for k, dec in pydantic_decorators.computed_fields.items()
    }


def is_pydantic_v2(module: ModuleType) -> bool:
    """Determine if the given module is pydantic v2.

    Given a module we expect to be a pydantic version, determine if it is pydantic v2.

    Args:
        module: A module.

    Returns:
        True if the module is pydantic v2, otherwise False.
    """
    return bool(module.__version__.startswith("2."))

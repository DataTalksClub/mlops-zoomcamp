from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from litestar.constants import SKIP_VALIDATION_NAMES
from litestar.exceptions import ImproperlyConfiguredException
from litestar.params import DependencyKwarg
from litestar.types import Empty, TypeDecodersSequence

if TYPE_CHECKING:
    from litestar.typing import FieldDefinition
    from litestar.utils.signature import ParsedSignature


__all__ = ("_validate_signature_dependencies", "_normalize_annotation", "_get_decoder_for_type")


def _validate_signature_dependencies(
    dependency_name_set: set[str], fn_name: str, parsed_signature: ParsedSignature
) -> set[str]:
    """Validate dependencies of ``parsed_signature``.

    Args:
        dependency_name_set: A set of dependency names
        fn_name: A callable's name.
        parsed_signature: A parsed signature.

    Returns:
        A set of validated dependency names.
    """
    dependency_names: set[str] = set(dependency_name_set)

    for parameter in parsed_signature.parameters.values():
        if isinstance(parameter.kwarg_definition, DependencyKwarg) and parameter.name not in dependency_name_set:
            if not parameter.is_optional and parameter.default is Empty:
                raise ImproperlyConfiguredException(
                    f"Explicit dependency '{parameter.name}' for '{fn_name}' has no default value, "
                    f"or provided dependency."
                )
            dependency_names.add(parameter.name)
    return dependency_names


def _normalize_annotation(field_definition: FieldDefinition) -> Any:
    if field_definition.name in SKIP_VALIDATION_NAMES or (
        isinstance(field_definition.kwarg_definition, DependencyKwarg)
        and field_definition.kwarg_definition.skip_validation
    ):
        return Any

    return field_definition.annotation


def _get_decoder_for_type(target_type: Any, type_decoders: TypeDecodersSequence) -> Callable[[type, Any], Any] | None:
    return next(
        (decoder for predicate, decoder in type_decoders if predicate(target_type)),
        None,
    )

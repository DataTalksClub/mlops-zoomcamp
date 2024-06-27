from typing import Any, Dict, List, Optional, Type

from typing_extensions import NotRequired, TypedDict


def truthy(o: Any) -> Optional[bool]:
    """Check if string or other obj is truthy."""
    if isinstance(o, str):
        if o.lower() in {"y", "yes", "t", "true", "1"}:
            return True
        elif o.lower() in {"n", "no", "f", "false", "0"}:
            return False
        else:
            return None
    elif o is None:
        return None
    else:
        return bool(o)


def method_is_from_subclass_of(cls: Type[object], base_cls: Type[object], method_name: str) -> bool:
    """
    Check to see whether a class's method comes from a subclass of some base class.

    This is used under the hood to see whether we would expect a patched RichCommand's help text
    methods to be compatible or incompatible with rich-click or not.
    """
    return any(
        getattr(c, method_name, None) == getattr(cls, method_name) for c in cls.__mro__ if issubclass(c, base_cls)
    )


class CommandGroupDict(TypedDict):
    """Specification for command groups."""

    name: NotRequired[str]
    commands: List[str]
    table_styles: NotRequired[Dict[str, Any]]
    panel_styles: NotRequired[Dict[str, Any]]


class OptionGroupDict(TypedDict):
    """Specification for option groups."""

    name: NotRequired[str]
    options: NotRequired[List[str]]
    table_styles: NotRequired[Dict[str, Any]]
    panel_styles: NotRequired[Dict[str, Any]]

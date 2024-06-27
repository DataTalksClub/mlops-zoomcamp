from ._core import (
    DecodeError,
    EncodeError,
    Field as _Field,
    Meta,
    MsgspecError,
    Raw,
    Struct,
    UnsetType,
    UNSET,
    NODEFAULT,
    ValidationError,
    defstruct,
    convert,
    to_builtins,
)


def field(*, default=NODEFAULT, default_factory=NODEFAULT, name=None):
    return _Field(default=default, default_factory=default_factory, name=name)


def from_builtins(
    obj,
    type,
    *,
    str_keys=False,
    str_values=False,
    builtin_types=None,
    dec_hook=None,
):
    """DEPRECATED: use ``msgspec.convert`` instead"""
    import warnings

    warnings.warn(
        "`msgspec.from_builtins` is deprecated, please use `msgspec.convert` instead",
        stacklevel=2,
    )
    return convert(
        obj,
        type,
        strict=not str_values,
        dec_hook=dec_hook,
        builtin_types=builtin_types,
        str_keys=str_keys,
    )


field.__doc__ = _Field.__doc__


from . import msgpack
from . import json
from . import yaml
from . import toml
from . import inspect
from . import structs
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

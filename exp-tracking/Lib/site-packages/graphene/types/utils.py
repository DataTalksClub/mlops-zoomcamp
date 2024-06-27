import inspect
from functools import partial

from ..utils.module_loading import import_string
from .mountedtype import MountedType
from .unmountedtype import UnmountedType


def get_field_as(value, _as=None):
    """
    Get type mounted
    """
    if isinstance(value, MountedType):
        return value
    elif isinstance(value, UnmountedType):
        if _as is None:
            return value
        return _as.mounted(value)


def yank_fields_from_attrs(attrs, _as=None, sort=True):
    """
    Extract all the fields in given attributes (dict)
    and return them ordered
    """
    fields_with_names = []
    for attname, value in list(attrs.items()):
        field = get_field_as(value, _as)
        if not field:
            continue
        fields_with_names.append((attname, field))

    if sort:
        fields_with_names = sorted(fields_with_names, key=lambda f: f[1])
    return dict(fields_with_names)


def get_type(_type):
    if isinstance(_type, str):
        return import_string(_type)
    if inspect.isfunction(_type) or isinstance(_type, partial):
        return _type()
    return _type


def get_underlying_type(_type):
    """Get the underlying type even if it is wrapped in structures like NonNull"""
    while hasattr(_type, "of_type"):
        _type = _type.of_type
    return _type

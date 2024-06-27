from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any
from typing import Callable

from dynaconf.base import RESERVED_ATTRS
from dynaconf.base import Settings
from dynaconf.loaders.base import SourceMetadata

__all__ = [
    "hookable",
    "EMPTY_VALUE",
    "Hook",
    "EagerValue",
    "HookValue",
    "MethodValue",
    "Action",
    "HookableSettings",
]


class Empty: ...


EMPTY_VALUE = Empty()


def hookable(function=None, name=None):
    """Adds before and after hooks to any method.

    :param function: function to be decorated
    :param name: name of the method to be decorated (default to method name)
    :return: decorated function

    Usage:

        class MyHookableClass(Settings):
            @hookable
            def execute_loaders(....):
                # do whatever you want here
                return super().execute_loaders(....)

        settings = Dynaconf(_wrapper_class=MyHookableClass)

        def hook_function(temp_settings, value, ...):
            # do whatever you want here
            return value

        settings.add_hook("after_execute_loaders", Hook(function))

        settings.FOO
        # will trigger execute_loaders
        # -> will trigger the hookable method
        # -> will execute registered hooks

    see tests/test_hooking.py for more examples.
    """

    if function and not callable(function):
        raise TypeError("hookable must be applied with named arguments only")

    def dispatch(fun, self, *args, **kwargs):
        """calls the decorated function and its hooks"""

        # if object has no hooks, return the original
        if not (_registered_hooks := get_hooks(self)):
            return fun(self, *args, **kwargs)

        function_name = name or fun.__name__

        # function being called not in the list of hooks, return the original
        if not set(_registered_hooks).intersection(
            (f"before_{function_name}", f"after_{function_name}")
        ):
            return fun(self, *args, **kwargs)

        # Create an unhookable (to avoid recursion)
        # temporary settings to pass to the hooked function
        temp_settings = Settings(
            dynaconf_skip_loaders=True,
            dynaconf_skip_validators=True,
        )
        allowed_keys = self.__dict__.keys() - set(RESERVED_ATTRS)
        temp_data = {
            k: v for k, v in self.__dict__.items() if k in allowed_keys
        }
        temp_settings._store.update(temp_data)

        def _hook(action: str, value: HookValue) -> HookValue:
            """executes the hooks for the given action"""
            hooks = _registered_hooks.get(f"{action}_{function_name}", [])
            for hook in hooks:
                value = hook.function(temp_settings, value, *args, **kwargs)
                value = HookValue.new(value)
            return value

        # Value starts as en empty value on the first before hook
        value = _hook("before", HookValue(EMPTY_VALUE))

        # If the value is EagerValue, it means main function should not be
        # executed and the value should go straight to the after hooks if any
        original_value = EMPTY_VALUE
        if not isinstance(value, EagerValue):
            value = MethodValue(fun(self, *args, **kwargs))
            original_value = value.value

        value = _hook("after", value)

        # track the loading history
        # adding inspect history like:
        # "identifier": "get_hook_(read_settings_from_cache_or_db)"
        if value.value != original_value and function_name == "get":
            hook_names = "_".join(
                [
                    hook.function.__name__
                    for list_of_hooks in _registered_hooks.values()
                    for hook in list_of_hooks
                ]
            )
            metadata = SourceMetadata(
                loader="hooking",
                identifier=f"{function_name}_hook_({hook_names})",
                merged=True,
            )
            history = self._loaded_by_loaders.setdefault(metadata, {})
            key = args[0] if args else kwargs.get("key")
            history[key] = value.value

        # unwrap the value from the HookValue so it can be returned
        # normally to the caller
        return value.value

    if function:
        # decorator applied without parameters e.g: @hookable
        @wraps(function)
        def wrapper(*args, **kwargs):
            return dispatch(function, *args, **kwargs)

        wrapper.original_function = function
        return wrapper

    def decorator(function):
        # decorator applied with parameters e.g: @hookable(before=False)
        @wraps(function)
        def wrapper(*args, **kwargs):
            return dispatch(function, *args, **kwargs)

        wrapper.original_function = function
        return wrapper

    return decorator


def get_hooks(obj):
    """get registered hooks from object
    must try different casing and accessors because of
    tests and casing mode set on dynaconf.
    """
    attr = "_registered_hooks"
    for key in [attr, attr.upper()]:
        if hasattr(obj, key):
            return getattr(obj, key)
        elif isinstance(obj, dict) and key in obj:
            return obj[key]
        elif hasattr(obj, "_store") and key in obj._store:
            return obj._store[key]
    return {}


@dataclass
class Hook:
    """Hook to wrap a callable on _registered_hooks list.

    :param callable: The callable to be wrapped

    The callable must accept the following arguments:

    - temp_settings: Settings or a Dict
    - value: The value to be processed wrapper in a HookValue
      (accumulated from previous hooks, last hook will receive the final value)
    - *args: The args passed to the original method
    - **kwargs: The kwargs passed to the original method

    The callable must return the value:

    - value: The processed value to be passed to the next hook
    """

    function: Callable


@dataclass
class HookValue:
    """Base class for hook values.
    Hooks must return a HookValue instance.
    """

    value: Any

    @classmethod
    def new(cls, value: Any) -> HookValue:
        """Return a new HookValue instance with the given value."""
        if isinstance(value, HookValue):
            return value
        return cls(value)

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        return self.value == other

    def __ne__(self, other) -> bool:
        return self.value != other

    def __bool__(self) -> bool:
        return bool(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __getitem__(self, item):
        return self.value[item]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __delitem__(self, key):
        del self.value[key]

    def __contains__(self, item):
        return item in self.value

    def __getattr__(self, item):
        return getattr(self.value, item)

    def __setattr__(self, key, value):
        if key == "value":
            super().__setattr__(key, value)
        else:
            setattr(self.value, key, value)

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __mul__(self, other):
        return self.value * other

    def __truediv__(self, other):
        return self.value / other

    def __floordiv__(self, other):
        return self.value // other

    def __mod__(self, other):
        return self.value % other

    def __divmod__(self, other):
        return divmod(self.value, other)

    def __pow__(self, power, modulo=None):
        return pow(self.value, power, modulo)

    def __delattr__(self, item):
        delattr(self.value, item)

    def __repr__(self) -> str:
        return repr(self.value)


class MethodValue(HookValue):
    """A value returned by a method
    The main decorated method have its value wrapped in this class
    """


class EagerValue(HookValue):
    """Use this wrapper to return earlier from a hook.
    Main function is bypassed and value is passed to after hooks."""


class Action(str, Enum):
    """All the hookable functions"""

    AFTER_GET = "after_get"
    BEFORE_GET = "before_get"


class HookableSettings(Settings):
    """Wrapper for dynaconf.base.Settings that adds hooks to get method."""

    _REGISTERED_HOOKS: dict[Action, list[Hook]] = {}
    # needed because django of Django admin see #1000

    @hookable
    def get(self, *args, **kwargs):
        return Settings.get(self, *args, **kwargs)

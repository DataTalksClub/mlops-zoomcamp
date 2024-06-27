from __future__ import annotations

import copy
import importlib
import inspect
import os
import warnings
from collections import defaultdict
from contextlib import contextmanager
from contextlib import suppress
from pathlib import Path
from typing import Any
from typing import Callable

from dynaconf import default_settings
from dynaconf.loaders import default_loader
from dynaconf.loaders import enable_external_loaders
from dynaconf.loaders import env_loader
from dynaconf.loaders import execute_instance_hooks
from dynaconf.loaders import execute_module_hooks
from dynaconf.loaders import py_loader
from dynaconf.loaders import settings_loader
from dynaconf.loaders import yaml_loader
from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils import BANNER
from dynaconf.utils import compat_kwargs
from dynaconf.utils import ensure_a_list
from dynaconf.utils import missing
from dynaconf.utils import object_merge
from dynaconf.utils import recursively_evaluate_lazy_format
from dynaconf.utils import RENAMED_VARS
from dynaconf.utils import upperfy
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils.files import find_file
from dynaconf.utils.files import glob
from dynaconf.utils.functional import empty
from dynaconf.utils.functional import LazyObject
from dynaconf.utils.parse_conf import apply_converter
from dynaconf.utils.parse_conf import boolean_fix
from dynaconf.utils.parse_conf import converters
from dynaconf.utils.parse_conf import Lazy
from dynaconf.utils.parse_conf import parse_conf_data
from dynaconf.utils.parse_conf import true_values
from dynaconf.validator import ValidationError
from dynaconf.validator import ValidatorList
from dynaconf.vendor.box.box_list import BoxList


class LazySettings(LazyObject):
    """Loads settings lazily from multiple sources:

        settings = Dynaconf(
            settings_files=["settings.toml"],  # path/glob
            environments=True,                 # activate layered environments
            envvar_prefix="MYAPP",             # `export MYAPP_FOO=bar`
            env_switcher="MYAPP_MODE",         # `export MYAPP_MODE=production`
            load_dotenv=True,                  # read a .env file
        )

    More options available on https://www.dynaconf.com/configuration/
    """

    def __init__(self, wrapped=None, **kwargs):
        """
        handle initialization for the customization cases

        :param wrapped: a deepcopy of this object will be wrapped (issue #596)
        :param kwargs: values that overrides default_settings
        """
        self._wrapper_class = kwargs.pop("_wrapper_class", Settings)
        self._warn_dynaconf_global_settings = kwargs.pop(
            "warn_dynaconf_global_settings", None
        )  # in 3.0.0 global settings is deprecated

        self.__resolve_config_aliases(kwargs)
        compat_kwargs(kwargs)
        self._kwargs = kwargs
        super().__init__()

        if wrapped:
            if self._django_override:
                # This fixes django issue #596
                self._wrapped = copy.deepcopy(wrapped)
            else:
                self._wrapped = wrapped

    def __resolve_config_aliases(self, kwargs):
        """takes aliases for _FOR_DYNACONF configurations

        e.g: ROOT_PATH='/' is transformed into `ROOT_PATH_FOR_DYNACONF`
        """

        misspells = {
            "settings_files": "settings_file",
            "SETTINGS_FILES": "SETTINGS_FILE",
            "environment": "environments",
            "ENVIRONMENT": "ENVIRONMENTS",
        }
        for misspell, correct in misspells.items():
            if misspell in kwargs:
                kwargs[correct] = kwargs.pop(misspell)

        for_dynaconf_keys = {
            key
            for key in UPPER_DEFAULT_SETTINGS
            if key.endswith("_FOR_DYNACONF")
        }
        aliases = {
            key.upper()
            for key in kwargs
            if f"{key.upper()}_FOR_DYNACONF" in for_dynaconf_keys
        }
        for alias in aliases:
            value = kwargs.pop(alias, empty)
            if value is empty:
                value = kwargs.pop(alias.lower())
            kwargs[f"{alias}_FOR_DYNACONF"] = value

    def __getattr__(self, name):
        """Allow getting keys from self.store using dot notation"""
        if self._wrapped is empty:
            self._setup()
        if name in self._wrapped._deleted:  # noqa
            raise AttributeError(
                f"Attribute {name} was deleted, " "or belongs to different env"
            )

        if name not in RESERVED_ATTRS:
            lowercase_mode = self._kwargs.get(
                "LOWERCASE_READ_FOR_DYNACONF",
                default_settings.LOWERCASE_READ_FOR_DYNACONF,
            )
            if lowercase_mode is True:
                name = name.upper()

        if (
            name.isupper()
            and (
                self._wrapped._fresh
                or name in self._wrapped.FRESH_VARS_FOR_DYNACONF
            )
            and name not in UPPER_DEFAULT_SETTINGS
        ):
            return self._wrapped.get_fresh(name)
        value = getattr(self._wrapped, name)
        if name not in RESERVED_ATTRS:
            return recursively_evaluate_lazy_format(value, self)
        return value

    def __call__(self, *args, **kwargs):
        """Allow direct call of settings('val')
        in place of settings.get('val')
        """
        return self.get(*args, **kwargs)

    @property
    def _should_load_dotenv(self):
        """Chicken and egg problem, we must manually check envvar
        before deciding if we are loading envvars :)"""
        _environ_load_dotenv = parse_conf_data(
            boolean_fix(os.environ.get("LOAD_DOTENV_FOR_DYNACONF")),
            tomlfy=True,
        )
        return self._kwargs.get("load_dotenv", _environ_load_dotenv)

    def _setup(self):
        """Initial setup, run once."""

        if self._warn_dynaconf_global_settings:
            warnings.warn(
                "Usage of `from dynaconf import settings` is now "
                "DEPRECATED in 3.0.0+. You are encouraged to change it to "
                "your own instance e.g: `settings = Dynaconf(*options)`",
                DeprecationWarning,
            )
            self._wrapper_class = Settings  # Force unhooked for this

        default_settings.reload(self._should_load_dotenv)
        environment_variable = self._kwargs.get(
            "ENVVAR_FOR_DYNACONF", default_settings.ENVVAR_FOR_DYNACONF
        )
        settings_module = os.environ.get(environment_variable)
        self._wrapped = self._wrapper_class(
            settings_module=settings_module, **self._kwargs
        )

    def configure(self, settings_module=None, **kwargs):
        """
        Allows user to reconfigure settings object passing a new settings
        module or separated kwargs

        :param settings_module: defines the settings file
        :param kwargs:  override default settings
        """
        default_settings.reload(self._should_load_dotenv)
        environment_var = self._kwargs.get(
            "ENVVAR_FOR_DYNACONF", default_settings.ENVVAR_FOR_DYNACONF
        )
        settings_module = settings_module or os.environ.get(environment_var)
        compat_kwargs(kwargs)
        kwargs.update(self._kwargs)
        self._wrapped = self._wrapper_class(
            settings_module=settings_module, **kwargs
        )

    @property
    def configured(self):
        """If wrapped is configured"""
        return self._wrapped is not empty


class Settings:
    """
    Common logic for settings whether set by a module or by the user.
    """

    dynaconf_banner = BANNER
    _store = DynaBox()

    def __init__(self, settings_module=None, **kwargs):  # pragma: no cover
        """Execute loaders and custom initialization

        :param settings_module: defines the settings file
        :param kwargs:  override default settings
        """
        self._fresh = False
        self._loaded_envs = []
        self._loaded_hooks = defaultdict(dict)
        self._loaded_py_modules = []
        self._loaded_files = []
        self._deleted = set()
        self._store = DynaBox(box_settings=self)
        self._env_cache = {}
        self._loaded_by_loaders: dict[SourceMetadata | str, Any] = {}
        self._loaders = []
        self._defaults = DynaBox(box_settings=self)
        self.environ = os.environ
        self.SETTINGS_MODULE = None
        self.filter_strategy = kwargs.get("filter_strategy", None)
        self._not_installed_warnings = []
        self._validate_only = kwargs.pop("validate_only", None)
        self._validate_exclude = kwargs.pop("validate_exclude", None)
        self._validate_only_current_env = kwargs.pop(
            "validate_only_current_env", False
        )

        self.validators = ValidatorList(
            self, validators=kwargs.pop("validators", None)
        )
        self._post_hooks: list[Callable] = ensure_a_list(
            kwargs.get("post_hooks", [])
        )

        compat_kwargs(kwargs)
        if settings_module:
            self.set(
                "SETTINGS_FILE_FOR_DYNACONF",
                settings_module,
                loader_identifier="init_settings_module",
            )
        for key, value in kwargs.items():
            self.set(
                key, value, loader_identifier="init_kwargs", validate=False
            )
        # execute loaders only after setting defaults got from kwargs
        self._defaults = kwargs

        # The following flags are used for when copying of settings is done
        skip_loaders = kwargs.get("dynaconf_skip_loaders", False)
        skip_validators = kwargs.get("dynaconf_skip_validators", False)

        if not skip_loaders:
            self.execute_loaders()

        if not skip_validators:
            self.validators.validate(
                only=self._validate_only,
                exclude=self._validate_exclude,
                only_current_env=self._validate_only_current_env,
            )

    def __call__(self, *args, **kwargs):
        """Allow direct call of `settings('val')`
        in place of `settings.get('val')`
        """
        return self.get(*args, **kwargs)

    def __setattr__(self, name, value):
        """Allow `settings.FOO = 'value'` while keeping internal attrs."""

        if name in RESERVED_ATTRS:
            super().__setattr__(name, value)
        else:
            self.set(name, value)

    def __delattr__(self, name):
        """stores reference in `_deleted` for proper error management"""
        self._deleted.add(name)
        if hasattr(self, name):
            super().__delattr__(name)

    def __contains__(self, item):
        """Respond to `item in settings`"""
        return item.upper() in self.store or item.lower() in self.store

    def __getattribute__(self, name):
        if (
            name.startswith("__")
            or name in RESERVED_ATTRS + UPPER_DEFAULT_SETTINGS
        ):
            return super().__getattribute__(name)

        # This is to keep the only upper case mode working
        # self._store has Lazy values already evaluated
        if (
            name.islower()
            and self._store.get("LOWERCASE_READ_FOR_DYNACONF", empty) is False
        ):
            try:
                # only matches exact casing, first levels always upper
                return self._store.__getattribute__(name)
            except KeyError:
                return super().__getattribute__(name)

        # then go to the regular .get which triggers hooks among other things
        value = self.get(name, default=empty)
        if value is empty:
            return super().__getattribute__(name)

        return value

    def __getitem__(self, item):
        """Allow getting variables as dict keys `settings['KEY']`"""
        value = self.get(item, default=empty)
        if value is empty:
            raise KeyError(f"{item} does not exist")
        return value

    def __setitem__(self, key, value):
        """Allow `settings['KEY'] = 'value'`"""
        self.set(key, value)

    @property
    def store(self):
        """Gets internal storage"""
        return self._store

    def __dir__(self):
        """Enable auto-complete for code editors"""
        return (
            RESERVED_ATTRS
            + [k.lower() for k in self.keys()]
            + list(self.keys())
        )

    def __iter__(self):
        """Redirects to store object"""
        yield from self._store

    def items(self):
        """Redirects to store object"""
        return self._store.items()

    def keys(self):
        """Redirects to store object"""
        return self.store.keys()

    def values(self):
        """Redirects to store object"""
        return self.store.values()

    def setdefault(
        self, item, default, apply_default_on_none=False, env: str = "unknown"
    ):
        """Returns value if exists or set it as the given default

        apply_default_on_none: if True, default is set when value is None
        env: used to create the source identifier
        """
        value = self.get(item, empty)

        # Yaml loader reads empty values as None, would we apply defaults?
        global_apply_default = (
            self.get("APPLY_DEFAULT_ON_NONE_FOR_DYNACONF") is not None
        )
        apply_default = default is not empty and (
            value is empty
            or (
                value is None
                and (
                    apply_default_on_none is True
                    or global_apply_default is True
                )
            )
        )
        loader_identifier = SourceMetadata("setdefault", "unique", env.lower())

        if apply_default:
            self.set(
                item,
                default,
                loader_identifier=loader_identifier,
                tomlfy=True,
            )
            return default

        return value

    def as_dict(self, env=None, internal=False):
        """Returns a dictionary with set key and values.

        :param env: Str env name, default self.current_env `DEVELOPMENT`
        :param internal: bool - should include dynaconf internal vars?
        """
        ctx_mgr = suppress() if env is None else self.using_env(env)
        with ctx_mgr:
            data = self.store.to_dict().copy()
            # if not internal remove internal settings
            if not internal:
                for name in UPPER_DEFAULT_SETTINGS:
                    data.pop(name, None)
            return data

    to_dict = as_dict  # backwards compatibility

    def _dotted_get(
        self, dotted_key, default=None, parent=None, cast=None, **kwargs
    ):
        """
        Perform dotted key lookups and keep track of where we are.
        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param parent: Is there a pre-loaded parent in a nested data?
        """
        # if parent is not traverseable raise error
        if parent and not hasattr(parent, "get"):
            raise AttributeError(
                f"cannot lookup {dotted_key!r} from {type(parent).__name__!r}"
            )

        split_key = dotted_key.split(".")
        name, keys = split_key[0], split_key[1:]
        result = self.get(name, default=default, parent=parent, **kwargs)

        # If we've reached the end, or parent key not found, then return result
        if not keys or result == default:
            if cast and cast in converters:
                return apply_converter(cast, result, box_settings=self)
            elif cast is True:
                return parse_conf_data(result, tomlfy=True, box_settings=self)
            return result

        # If we've still got key elements to traverse, let's do that.
        return self._dotted_get(
            ".".join(keys), default=default, parent=result, cast=cast, **kwargs
        )

    def get(
        self,
        key,
        default=None,
        cast=None,
        fresh=False,
        dotted_lookup=empty,
        parent=None,
        sysenv_fallback=None,
    ):
        """
        Get a value from settings store, this is the preferred way to access::

            >>> from dynaconf import settings
            >>> settings.get('KEY')

        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
        :param fresh: Should reload from loaders store before access?
        :param dotted_lookup: Should perform dotted-path lookup?
        :param parent: Is there a pre-loaded parent in a nested data?
        :param sysenv_fallback: Should fallback to system environ if not found?
        :return: The value if found, default or None
        """
        if sysenv_fallback is None:
            sysenv_fallback = self._store.get("SYSENV_FALLBACK_FOR_DYNACONF")

        nested_sep = self._store.get("NESTED_SEPARATOR_FOR_DYNACONF")
        if isinstance(key, str):
            if nested_sep and nested_sep in key:
                # turn FOO__bar__ZAZ in `FOO.bar.ZAZ`
                key = key.replace(nested_sep, ".")

            if dotted_lookup is empty:
                dotted_lookup = self._store.get("DOTTED_LOOKUP_FOR_DYNACONF")

            if "." in key and dotted_lookup:
                return self._dotted_get(
                    dotted_key=key,
                    default=default,
                    cast=cast,
                    fresh=fresh,
                    parent=parent,
                )

            key = upperfy(key)

        # handles system environment fallback
        if default is None:
            key_in_sysenv_fallback_list = isinstance(
                sysenv_fallback, list
            ) and key in [upperfy(k) for k in sysenv_fallback]
            if sysenv_fallback is True or key_in_sysenv_fallback_list:
                default = self.get_environ(key, cast=True)

        # default values should behave exactly Dynaconf parsed values
        if default is not None:
            if isinstance(default, list):
                default = BoxList(default)
            elif isinstance(default, dict):
                default = DynaBox(default)

        if key in self._deleted:
            return default

        if (
            fresh
            or self._fresh
            or key in getattr(self, "FRESH_VARS_FOR_DYNACONF", ())
        ) and key not in UPPER_DEFAULT_SETTINGS:
            self.unset(key)
            self.execute_loaders(key=key)

        data = (parent or self.store).get(key, default)
        if cast:
            data = apply_converter(cast, data, box_settings=self)
        return data

    def exists(self, key, fresh=False):
        """Check if key exists

        :param key: the name of setting variable
        :param fresh: if key should be taken from source directly
        :return: Boolean
        """
        key = upperfy(key)
        if key in self._deleted:
            return False
        return self.get(key, fresh=fresh, default=missing) is not missing

    def get_fresh(self, key, default=None, cast=None):
        """This is a shortcut to `get(key, fresh=True)`. always reload from
        loaders store before getting the var.

        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
        :return: The value if found, default or None
        """
        return self.get(key, default=default, cast=cast, fresh=True)

    def get_environ(self, key, default=None, cast=None):
        """Get value from environment variable using os.environ.get

        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
         or cast must be true to use cast inference
        :return: The value if found, default or None
        """
        key = upperfy(key)
        data = self.environ.get(key, default)
        if data:
            if cast in converters:
                data = apply_converter(cast, data, box_settings=self)
            elif cast is True:
                data = parse_conf_data(
                    boolean_fix(data), tomlfy=True, box_settings=self
                )
        return data

    def exists_in_environ(self, key):
        """Return True if env variable is exported"""
        return upperfy(key) in self.environ

    def as_bool(self, key):
        """Partial method for get with bool cast"""
        return self.get(key, cast="@bool")

    def as_int(self, key):
        """Partial method for get with int cast"""
        return self.get(key, cast="@int")

    def as_float(self, key):
        """Partial method for get with float cast"""
        return self.get(key, cast="@float")

    def as_json(self, key):
        """Partial method for get with json cast"""
        return self.get(key, cast="@json")

    @property
    def loaded_envs(self):
        """Get or create internal loaded envs list"""
        if not self._loaded_envs:
            self._loaded_envs = []
        return self._loaded_envs

    @loaded_envs.setter
    def loaded_envs(self, value):
        """Setter for env list"""
        self._loaded_envs = value

    # compat
    loaded_namespaces = loaded_envs

    @property
    def loaded_by_loaders(self):  # pragma: no cover
        """Gets the internal mapping of LOADER -> values"""
        return self._loaded_by_loaders

    def from_env(self, env="", keep=False, **kwargs):
        """Return a new isolated settings object pointing to specified env.

        Example of settings.toml::

            [development]
            message = 'This is in dev'
            [other]
            message = 'this is in other env'

        Program::

            >>> from dynaconf import settings
            >>> print(settings.MESSAGE)
            'This is in dev'
            >>> print(settings.from_env('other').MESSAGE)
            'This is in other env'
            # The existing settings object remains the same.
            >>> print(settings.MESSAGE)
            'This is in dev'

        Arguments:
            env {str} -- Env to load (development, production, custom)

        Keyword Arguments:
            keep {bool} -- Keep pre-existing values (default: {False})
            kwargs {dict} -- Passed directly to new instance.
        """
        cache_key = f"{env}_{keep}_{kwargs}"
        if cache_key in self._env_cache:
            return self._env_cache[cache_key]

        new_data = {
            key: self.get(key)
            for key in UPPER_DEFAULT_SETTINGS
            if key not in RENAMED_VARS
        }

        if self.filter_strategy:
            # Retain the filtering strategy when switching environments
            new_data["filter_strategy"] = self.filter_strategy

        # This is here for backwards compatibility
        # To be removed on 4.x.x
        default_settings_paths = self.get("default_settings_paths")
        if default_settings_paths:  # pragma: no cover
            new_data["default_settings_paths"] = default_settings_paths

        if keep:
            # keep existing values from current env
            new_data.update(
                {
                    key: value
                    for key, value in self.store.to_dict().copy().items()
                    if key.isupper() and key not in RENAMED_VARS
                }
            )

        new_data.update(kwargs)
        new_data["FORCE_ENV_FOR_DYNACONF"] = env
        new_settings = LazySettings(**new_data)
        self._env_cache[cache_key] = new_settings

        # update source metadata for inspecting
        self._loaded_by_loaders.update(new_settings._loaded_by_loaders)

        return new_settings

    @contextmanager
    def using_env(self, env, clean=True, silent=True, filename=None):
        """
        This context manager allows the contextual use of a different env
        Example of settings.toml::

            [development]
            message = 'This is in dev'
            [other]
            message = 'this is in other env'

        Program::

            >>> from dynaconf import settings
            >>> print settings.MESSAGE
            'This is in dev'
            >>> with settings.using_env('OTHER'):
            ...    print settings.MESSAGE
            'this is in other env'

        :param env: Upper case name of env without any _
        :param clean: If preloaded vars should be cleaned
        :param silent: Silence errors
        :param filename: Custom filename to load (optional)
        :return: context
        """
        try:
            self.setenv(env, clean=clean, silent=silent, filename=filename)
            yield
        finally:
            if env.lower() != self.ENV_FOR_DYNACONF.lower():
                del self.loaded_envs[-1]
            self.setenv(self.current_env, clean=clean, filename=filename)

    # compat
    using_namespace = using_env

    @contextmanager
    def fresh(self):
        """
        this context manager force the load of a key direct from the store::

            $ export DYNACONF_VALUE='Original'
            >>> from dynaconf import settings
            >>> print settings.VALUE
            'Original'
            $ export DYNACONF_VALUE='Changed Value'
            >>> print settings.VALUE  # will not be reloaded from env vars
            'Original
            >>> with settings.fresh(): # inside this context all is reloaded
            ...    print settings.VALUE
            'Changed Value'

        an alternative is using `settings.get_fresh(key)`

        :return: context
        """

        self._fresh = True
        yield
        self._fresh = False

    @property
    def current_env(self):
        """Return the current active env"""

        if self.ENVIRONMENTS_FOR_DYNACONF is False:
            return self.MAIN_ENV_FOR_DYNACONF.lower()

        if self.FORCE_ENV_FOR_DYNACONF is not None:
            self.ENV_FOR_DYNACONF = self.FORCE_ENV_FOR_DYNACONF
            return self.FORCE_ENV_FOR_DYNACONF

        try:
            return self.loaded_envs[-1]
        except IndexError:
            return self.ENV_FOR_DYNACONF

    # compat
    current_namespace = current_env

    @property
    def settings_module(self):
        """Gets SETTINGS_MODULE variable"""
        settings_module = parse_conf_data(
            os.environ.get(
                self.ENVVAR_FOR_DYNACONF, self.SETTINGS_FILE_FOR_DYNACONF
            ),
            tomlfy=True,
            box_settings=self,
        )
        if settings_module != getattr(self, "SETTINGS_MODULE", None):
            self.set(
                "SETTINGS_MODULE",
                settings_module,
                loader_identifier="settings_module_method",
            )

        # This is for backewards compatibility, to be removed on 4.x.x
        if not self.SETTINGS_MODULE and self.get("default_settings_paths"):
            self.SETTINGS_MODULE = self.get("default_settings_paths")

        return self.SETTINGS_MODULE

    # Backwards compatibility see #169
    settings_file = settings_module

    def setenv(self, env=None, clean=True, silent=True, filename=None):
        """Used to interactively change the env
        Example of settings.toml::

            [development]
            message = 'This is in dev'
            [other]
            message = 'this is in other env'

        Program::

            >>> from dynaconf import settings
            >>> print settings.MESSAGE
            'This is in dev'
            >>> with settings.using_env('OTHER'):
            ...    print settings.MESSAGE
            'this is in other env'

        :param env: Upper case name of env without any _
        :param clean: If preloaded vars should be cleaned
        :param silent: Silence errors
        :param filename: Custom filename to load (optional)
        :return: context
        """
        env = env or self.ENV_FOR_DYNACONF

        if not isinstance(env, str) or " " in env:
            raise ValueError("env should be a string without spaces")

        env = env.upper()

        if env != self.ENV_FOR_DYNACONF:
            self.loaded_envs.append(env)
        else:
            self.loaded_envs = []

        if clean:
            self.clean(env=env)
        self.execute_loaders(env=env, silent=silent, filename=filename)

    # compat
    namespace = setenv

    def clean(self, *args, **kwargs):
        """Clean all loaded values to reload when switching envs"""
        for key in list(self.store.keys()):
            self.unset(key)

    def unset(self, key, force=False):
        """Unset on all references

        :param key: The key to be unset
        :param force: Bypass default checks and force unset
        """
        key = upperfy(key.strip())
        if (
            key not in UPPER_DEFAULT_SETTINGS
            and key not in self._defaults
            or force
        ):
            with suppress(KeyError, AttributeError):
                # AttributeError can happen when a LazyValue consumes
                # a previously deleted key
                delattr(self, key)
                del self.store[key]

    def unset_all(self, keys, force=False):  # pragma: no cover
        """Unset based on a list of keys

        :param keys: a list of keys
        :param force: Bypass default checks and force unset
        """
        for key in keys:
            self.unset(key, force=force)

    def _dotted_set(
        self, dotted_key, value, tomlfy=False, validate=empty, **kwargs
    ):
        """Sets dotted keys as nested dictionaries.

        Dotted set will always reassign the value, to merge use `@merge` token

        Arguments:
            dotted_key {str} -- A traversal name e.g: foo.bar.zaz
            value {Any} -- The value to set to the nested value.

        Keyword Arguments:
            tomlfy {bool} -- Perform toml parsing (default: {False})
            validate {bool} --
        """
        if validate is empty:
            validate = self.get(
                "VALIDATE_ON_UPDATE_FOR_DYNACONF"
            )  # pragma: nocover

        split_keys = dotted_key.split(".")
        existing_data = self.get(split_keys[0], {})
        new_data = tree = DynaBox(box_settings=self)

        for k in split_keys[:-1]:
            tree = tree.setdefault(k, {})

        value = parse_conf_data(value, tomlfy=tomlfy, box_settings=self)
        tree[split_keys[-1]] = value

        if existing_data:
            old_data = DynaBox(
                {split_keys[0]: existing_data}, box_settings=self
            )
            new_data = object_merge(
                old=old_data,
                new=new_data,
                full_path=split_keys,
            )
        self.update(data=new_data, tomlfy=tomlfy, validate=validate, **kwargs)

    def set(
        self,
        key,
        value,
        loader_identifier: SourceMetadata | str | None = None,
        tomlfy=False,
        dotted_lookup=empty,
        is_secret="DeprecatedArgument",  # noqa
        validate=empty,
        merge=empty,
    ):
        """Set a value storing references for the loader

        :param key: The key to store. Can be of any type.
        :param value: The raw value to parse and store
        :param loader_identifier: Optional loader name e.g: toml, yaml etc.
                                  Or instance of SourceMetadata
        :param tomlfy: Bool define if value is parsed by toml (defaults False)
        :param merge: Bool define if existing nested data will be merged.
        :param validate: Bool define if validation will be triggered
        """

        # Ensure source_metadata always is set even if set is called
        # without a loader_identifier
        if isinstance(loader_identifier, str) or loader_identifier is None:
            source_metadata = SourceMetadata(
                loader="set_method",
                identifier=loader_identifier or "undefined",
                merged=merge is True,
            )
        else:  # loader identifier must be a SourceMetadata instance
            source_metadata = loader_identifier

        if validate is empty:
            validate = self.get("VALIDATE_ON_UPDATE_FOR_DYNACONF")
        if dotted_lookup is empty:
            dotted_lookup = self.get("DOTTED_LOOKUP_FOR_DYNACONF")
        nested_sep = self.get("NESTED_SEPARATOR_FOR_DYNACONF")

        if isinstance(key, str):
            if nested_sep and nested_sep in key:
                key = key.replace(nested_sep, ".")  # FOO__bar -> FOO.bar

            if "." in key and dotted_lookup is True:
                return self._dotted_set(
                    key,
                    value,
                    loader_identifier=source_metadata,
                    tomlfy=tomlfy,
                    validate=validate,
                )
            key = upperfy(key.strip())

        parsed = parse_conf_data(value, tomlfy=tomlfy, box_settings=self)

        # Fix for #869 - The call to getattr trigger early evaluation
        existing = (
            self.store.get(key, None) if not isinstance(parsed, Lazy) else None
        )

        if getattr(parsed, "_dynaconf_del", None):
            self.unset(key, force=True)  # `@del` in a first level var.
            return

        if getattr(parsed, "_dynaconf_reset", False):  # pragma: no cover
            parsed = parsed.unwrap()  # `@reset` in a first level var.

        if getattr(parsed, "_dynaconf_merge_unique", False):
            # `@merge_unique` in a first level var
            if existing:
                # update SourceMetadata (for inspecting purposes)
                source_metadata = source_metadata._replace(merged=True)
                parsed = object_merge(existing, parsed.unwrap(), unique=True)
            else:
                parsed = parsed.unwrap()

        if getattr(parsed, "_dynaconf_merge", False):
            # `@merge` in a first level var
            if existing:
                # update SourceMetadata (for inspecting purposes)
                source_metadata = source_metadata._replace(merged=True)
                parsed = object_merge(existing, parsed.unwrap())
            else:
                parsed = parsed.unwrap()

        should_merge = existing is not None and existing != parsed
        if should_merge:
            # `dynaconf_merge` used in file root `merge=True`
            if merge and merge is not empty:
                source_metadata = source_metadata._replace(merged=True)
                parsed = object_merge(existing, parsed)
            else:
                # `dynaconf_merge` may be used within the key structure
                # Or merge_enabled is set to True
                parsed, source_metadata = self._merge_before_set(
                    existing, parsed, source_metadata, context_merge=merge
                )

        if isinstance(parsed, dict) and not isinstance(parsed, DynaBox):
            parsed = DynaBox(parsed, box_settings=self)

        # Set the parsed value
        self.store[key] = parsed
        self._deleted.discard(key)

        # check if str because we can't directly set/get non-str with obj. e.g.
        #     setting.1
        #     settings.(1,2)
        if isinstance(key, str):
            super().__setattr__(key, parsed)

        # Track history for inspect, store the raw_value
        if source_metadata in self._loaded_by_loaders:
            self._loaded_by_loaders[source_metadata][key] = value
        else:
            self._loaded_by_loaders[source_metadata] = {key: value}

        if loader_identifier is None:
            # if .set is called without loader identifier it becomes
            # a default value and goes away only when explicitly unset
            self._defaults[key] = parsed

        if validate is True:
            self.validators.validate()

    def update(
        self,
        data=None,
        loader_identifier=None,
        tomlfy=False,
        merge=empty,
        is_secret="DeprecatedArgument",  # noqa
        dotted_lookup=empty,
        validate=empty,
        **kwargs,
    ):
        """
        Update values in the current settings object without saving in stores::

            >>> from dynaconf import settings
            >>> print settings.NAME
            'Bruno'
            >>> settings.update({'NAME': 'John'}, other_value=1)
            >>> print settings.NAME
            'John'
            >>> print settings.OTHER_VALUE
            1

        :param data: Data to be updated
        :param loader_identifier: Only to be used by custom loaders
        :param tomlfy: Bool define if value is parsed by toml (defaults False)
        :param merge: Bool define if existing nested data will be merged.
        :param validate: Bool define if validators will trigger automatically
        :param kwargs: extra values to update
        :return: None
        """

        if validate is empty:
            validate = self.get("VALIDATE_ON_UPDATE_FOR_DYNACONF")

        data = data or {}
        data.update(kwargs)
        for key, value in data.items():
            # update() will handle validation later
            with suppress(ValidationError):
                self.set(
                    key,
                    value,
                    loader_identifier=loader_identifier,
                    tomlfy=tomlfy,
                    merge=merge,
                    dotted_lookup=dotted_lookup,
                    validate=validate,
                )

        # handle param `validate`
        if validate is True:
            self.validators.validate()
        elif validate == "all":
            self.validators.validate_all()

    def _merge_before_set(
        self,
        existing,
        value,
        identifier: SourceMetadata | None = None,
        context_merge=empty,
    ):
        """
        Merge the new value being set with the existing value before set
        Returns the merged value and the updated identifier (for inspecting).
        """
        # context_merge may come from file_scope or env_scope
        if context_merge is empty:
            context_merge = self.get("MERGE_ENABLED_FOR_DYNACONF")

        if isinstance(value, dict):
            local_merge = value.pop(
                "dynaconf_merge", value.pop("dynaconf_merge_unique", None)
            )
            if local_merge not in (True, False, None) and not value:
                # In case `dynaconf_merge:` holds value not boolean - ref #241
                value = local_merge

            if local_merge or (context_merge and local_merge is not False):
                identifier = (
                    identifier._replace(merged=True) if identifier else None
                )
                value = object_merge(existing, value)

        if isinstance(value, (list, tuple)):
            value = list(value)
            local_merge = None
            unique = False
            if "dynaconf_merge" in value:
                value.remove("dynaconf_merge")
                local_merge = True
            elif "dynaconf_merge_unique" in value:
                value.remove("dynaconf_merge_unique")
                local_merge = True
                unique = True

            if local_merge or (context_merge and local_merge is not False):
                identifier = (
                    identifier._replace(merged=True) if identifier else None
                )
                value = object_merge(existing, value, unique=unique)
        return value, identifier

    @property
    def loaders(self):  # pragma: no cover
        """Return available loaders"""
        if self.LOADERS_FOR_DYNACONF in (None, 0, "0", "false", False):
            return []

        if not self._loaders:
            self._loaders = self.LOADERS_FOR_DYNACONF

        return [importlib.import_module(loader) for loader in self._loaders]

    def reload(self, env=None, silent=None):  # pragma: no cover
        """Clean end Execute all loaders"""
        self.clean()
        self._loaded_hooks.clear()
        self.execute_loaders(env, silent)

    def execute_loaders(
        self, env=None, silent=None, key=None, filename=None, loaders=None
    ):
        """Execute all internal and registered loaders

        :param env: The environment to load
        :param silent: If loading errors is silenced
        :param key: if provided load a single key
        :param filename: optional custom filename to load
        :param loaders: optional list of loader modules
        """
        if key is None:
            default_loader(self, self._defaults)

        env = (env or self.current_env).upper()
        silent = silent or self.SILENT_ERRORS_FOR_DYNACONF

        if loaders is None:
            self.pre_load(env, silent=silent, key=key)
            settings_loader(
                self, env=env, silent=silent, key=key, filename=filename
            )
            self.load_extra_yaml(env, silent, key)  # DEPRECATED
            enable_external_loaders(self)

            loaders = self.loaders
        # non setting_file or py_module loaders
        for core_loader in loaders:
            core_loader.load(self, env, silent=silent, key=key)

        self.load_includes(env, silent=silent, key=key)

        # execute hooks
        execute_module_hooks("post", self, env, silent=silent, key=key)
        execute_instance_hooks(self, "post", self._post_hooks)

    def pre_load(self, env, silent, key):
        """Do we have any file to pre-load before main settings file?"""
        preloads = self.get("PRELOAD_FOR_DYNACONF", [])
        if preloads:
            self.load_file(path=preloads, env=env, silent=silent, key=key)

    def load_includes(self, env, silent, key):
        """Do we have any nested includes we need to process?"""
        includes = ensure_a_list(self.get("DYNACONF_INCLUDE"))
        includes.extend(ensure_a_list(self.get("INCLUDES_FOR_DYNACONF")))
        if includes:
            self.load_file(path=includes, env=env, silent=silent, key=key)
            # ensure env vars are the last thing loaded after all includes
            last_loader = self.loaders and self.loaders[-1]
            if last_loader and last_loader == env_loader:
                last_loader.load(self, env, silent, key)

    def load_file(
        self, path=None, env=None, silent=True, key=None, validate=empty
    ):
        """Programmatically load files from ``path``.

        When using relative paths, the basedir fallbacks in this order:
        - ROOT_PATH_FOR_DYNACONF
        - Directory of the last loaded file
        - CWD

        :param path: A single filename or a file list
        :param env: Which env to load from file (default current_env)
        :param silent: Should raise errors?
        :param key: Load a single key?
        :param validate: Should trigger validation?
        """
        if validate is empty:
            validate = self.get("VALIDATE_ON_UPDATE_FOR_DYNACONF")

        env = (env or self.current_env).upper()
        files = ensure_a_list(path)
        if files:
            already_loaded = set()
            for _filename in files:
                # load_file() will handle validation later
                with suppress(ValidationError):
                    if py_loader.try_to_load_from_py_module_name(
                        obj=self, name=_filename, silent=True
                    ):
                        # if it was possible to load from module name
                        # continue the loop.
                        continue

                root_dir = str(self._root_path or os.getcwd())

                # Issue #494
                if (
                    isinstance(_filename, Path)
                    and str(_filename.parent) in root_dir
                ):  # pragma: no cover
                    filepath = str(_filename)
                else:
                    filepath = os.path.join(root_dir, str(_filename))

                paths = [
                    p for p in sorted(glob(filepath)) if ".local." not in p
                ]
                local_paths = [
                    p for p in sorted(glob(filepath)) if ".local." in p
                ]

                # Handle possible *.globs sorted alphanumeric
                for path in paths + local_paths:
                    if path in already_loaded:  # pragma: no cover
                        continue

                    # load_file() will handle validation later
                    with suppress(ValidationError):
                        settings_loader(
                            obj=self,
                            env=env,
                            silent=silent,
                            key=key,
                            filename=path,
                            validate=validate,
                        )
                        already_loaded.add(path)

        # handle param `validate`
        if validate is True:
            self.validators.validate()
        elif validate == "all":
            self.validators.validate_all()

    @property
    def _root_path(self):
        """ROOT_PATH_FOR_DYNACONF or the path of first loaded file or '.'"""

        if self.ROOT_PATH_FOR_DYNACONF is not None:
            return self.ROOT_PATH_FOR_DYNACONF

        if self._loaded_files:  # called once
            root_path = os.path.dirname(self._loaded_files[0])
            self.set(
                "ROOT_PATH_FOR_DYNACONF",
                root_path,
                loader_identifier="_root_path",
            )
            return root_path

    def load_extra_yaml(self, env, silent, key):
        """This is deprecated, kept for compat

        .. deprecated:: 1.0.0
            Use multiple settings or INCLUDES_FOR_DYNACONF files instead.
        """
        if self.get("YAML") is not None:
            warnings.warn(
                "The use of YAML var is deprecated, please define multiple "
                "filepaths instead: "
                "e.g: SETTINGS_FILE_FOR_DYNACONF = "
                "'settings.py,settings.yaml,settings.toml' or "
                "INCLUDES_FOR_DYNACONF=['path.toml', 'folder/*']"
            )
            yaml_loader.load(
                self,
                env=env,
                filename=self.find_file(self.get("YAML")),
                silent=silent,
                key=key,
            )

    def path_for(self, *args):
        """Path containing _root_path"""
        if args and args[0].startswith(os.path.sep):
            return os.path.join(*args)
        return os.path.join(self._root_path or os.getcwd(), *args)

    def find_file(self, *args, **kwargs):
        kwargs.setdefault("project_root", self._root_path)
        kwargs.setdefault(
            "skip_files", self.get("SKIP_FILES_FOR_DYNACONF", [])
        )
        return find_file(*args, **kwargs)

    def flag(self, key, env=None):
        """Feature flagging system
        write flags to redis
        $ dynaconf write redis -s DASHBOARD=1 -e premiumuser
        meaning: Any premium user has DASHBOARD feature enabled

        In your program do::

            # premium user has access to dashboard?
            >>> if settings.flag('dashboard', 'premiumuser'):
            ...     activate_dashboard()

        The value is ensured to be loaded fresh from redis server

        It also works with file settings but the recommended is redis
        as the data can be loaded once it is updated.

        :param key: The flag name
        :param env: The env to look for
        """
        env = env or self.ENVVAR_PREFIX_FOR_DYNACONF or "DYNACONF"
        with self.using_env(env):
            value = self.get_fresh(key)
            return value is True or value in true_values

    def populate_obj(self, obj, keys=None, ignore=None):
        """Given the `obj` populate it using self.store items.

        :param obj: An object to be populated, a class instance.
        :param keys: A list of keys to be included.
        :param ignore: A list of keys to be excluded.
        """
        keys = keys or self.keys()
        for key in keys:
            key = upperfy(key)
            if ignore and key in ignore:
                continue
            value = self.get(key, empty)
            if value is not empty:
                setattr(obj, key, value)

    def dynaconf_clone(self):
        """Clone the current settings object."""
        try:
            return copy.deepcopy(self)
        except (TypeError, copy.Error):
            # can't deepcopy settings object because of module object
            # being set as value in the settings dict
            new_data = self.to_dict(internal=True)
            new_data["dynaconf_skip_loaders"] = True
            new_data["dynaconf_skip_validators"] = True
            new_data["_registered_hooks"] = {}
            new_data["_REGISTERED_HOOKS"] = {}
            return self.__class__(**new_data)

    @property
    def dynaconf(self):
        """A proxy to access internal methods and attributes

        Starting in 3.0.0 Dynaconf now allows first level lower case
        keys that are not reserved keyword, so this is a proxy to
        internal methods and attrs.
        """

        class AttrProxy:
            def __init__(self, obj):
                self.obj = obj

            def __getattr__(self, name):
                return getattr(self.obj, f"dynaconf_{name}")

        return AttrProxy(self)

    @property
    def logger(self):  # pragma: no cover
        """backwards compatibility with pre 3.0 loaders
        In dynaconf 3.0.0 logger and debug messages has been removed.
        """
        warnings.warn(
            "logger and DEBUG messages has been removed on dynaconf 3.0.0"
        )
        import logging  # noqa

        return logging.getLogger("dynaconf")

    def is_overridden(self, setting):  # noqa
        """This is to provide Django DJDT support: issue 382"""
        return False


"""Upper case default settings"""
UPPER_DEFAULT_SETTINGS = [k for k in dir(default_settings) if k.isupper()]

"""Attributes created on Settings before 3.0.0"""
RESERVED_ATTRS = (
    [
        item[0]
        for item in inspect.getmembers(LazySettings)
        if not item[0].startswith("__")
    ]
    + [
        item[0]
        for item in inspect.getmembers(Settings)
        if not item[0].startswith("__")
    ]
    + [
        "_defaults",
        "_deleted",
        "_env_cache",
        "_fresh",
        "_kwargs",
        "_loaded_by_loaders",
        "_loaded_envs",
        "_loaded_hooks",
        "_loaded_py_modules",
        "_loaded_files",
        "_loaders",
        "_not_installed_warnings",
        "_store",
        "_warn_dynaconf_global_settings",
        "_should_load_dotenv",
        "environ",
        "SETTINGS_MODULE",
        "filter_strategy",
        "validators",
        "_validate_only",
        "_validate_exclude",
        "_validate_only_current_env",
        "_post_hooks",
        "_registered_hooks",
        "_REGISTERED_HOOKS",
    ]
)

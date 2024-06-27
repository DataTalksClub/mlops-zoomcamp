from __future__ import annotations

import importlib
import os
from typing import Callable
from typing import TYPE_CHECKING

from dynaconf import constants as ct
from dynaconf import default_settings
from dynaconf.loaders import ini_loader
from dynaconf.loaders import json_loader
from dynaconf.loaders import py_loader
from dynaconf.loaders import toml_loader
from dynaconf.loaders import yaml_loader
from dynaconf.utils import deduplicate
from dynaconf.utils import ensure_a_list
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils.files import get_local_filename
from dynaconf.utils.files import glob
from dynaconf.utils.files import has_magic
from dynaconf.utils.parse_conf import false_values

if TYPE_CHECKING:
    from dynaconf.base import Settings


def default_loader(obj, defaults=None):
    """Initial loader for the initialization process.

    Steps:
    - Load default settings (from static module) + kwargs overrides (together)
    - Load envvar overrides
    """
    # LOAD DEFAULT STATIC + KWARGS OVERRIDES

    defaults = defaults or {}
    default_settings_values = {
        key: value
        for key, value in default_settings.__dict__.items()  # noqa
        if key.isupper()
    }

    all_keys = deduplicate(
        list(defaults.keys()) + list(default_settings_values.keys())
    )

    for key in all_keys:
        if not obj.exists(key):
            value = defaults.get(key, default_settings_values.get(key))
            obj.set(
                key,
                value,
                loader_identifier="default_settings",
                validate=False,
            )

    # LOAD ENVVAR OVERRIDES

    # start dotenv to get default env vars from there
    # check overrides in env vars
    if obj.get("load_dotenv") is True:
        default_settings.start_dotenv(obj)

    # Deal with cases where a custom ENV_SWITCHER_IS_PROVIDED
    # Example: Flask and Django Extensions
    env_switcher = defaults.get(
        "ENV_SWITCHER_FOR_DYNACONF", "ENV_FOR_DYNACONF"
    )

    for key in all_keys:
        if key not in default_settings_values.keys():
            continue

        env_value = obj.get_environ(
            env_switcher if key == "ENV_FOR_DYNACONF" else key,
            default="_not_found",
        )

        if env_value != "_not_found":
            obj.set(
                key,
                env_value,
                tomlfy=True,
                loader_identifier="envvars_first_load",
            )


def execute_instance_hooks(
    obj: Settings, hook_type: str, hook_functions: list[Callable]
):
    """Execute hooks provided by Setting instance"""
    hook_source = "instance"
    for hook_func in hook_functions:
        _run_hook_function(obj, hook_type, hook_func, hook_source)


def execute_module_hooks(
    hook, obj, env=None, silent=True, key=None, modules=None, files=None
):
    """Execute dynaconf_hooks from module or filepath."""
    if hook not in ["post"]:
        raise ValueError(f"hook {hook} not supported yet.")

    # try to load hooks using python module __name__
    modules = modules or obj._loaded_py_modules
    for loaded_module in modules:
        hook_module_name = ".".join(
            loaded_module.split(".")[:-1] + ["dynaconf_hooks"]
        )
        try:
            hook_module = importlib.import_module(hook_module_name)
        except (ImportError, TypeError):
            # There was no hook on the same path as a python module
            continue
        else:
            _run_hook_module(
                hook_type=hook,
                hook_module=hook_module,
                obj=obj,
                key=key,
            )

    # Try to load from python filename path
    files = files or obj._loaded_files
    for loaded_file in files:
        hook_file = os.path.join(
            os.path.dirname(loaded_file), "dynaconf_hooks.py"
        )
        hook_module = py_loader.import_from_filename(
            obj, hook_file, silent=silent
        )
        if not hook_module:
            # There was no hook on the same path as a python file
            continue
        _run_hook_module(
            hook_type=hook,
            hook_module=hook_module,
            obj=obj,
            key=key,
        )


# alias
execute_hooks = execute_module_hooks


def _run_hook_module(hook_type, hook_module, obj, key=""):
    """
    Run a hook function from hook_module.

    Given a @hook_type, a @hook_module and a settings @obj, load the function
    and execute it if found.
    """
    hook_source = hook_module.__file__

    # check if already loaded
    if hook_type in obj._loaded_hooks.get(hook_source, {}):
        return

    # check errors
    if hook_module and getattr(hook_module, "_error", False):
        if not isinstance(hook_module._error, FileNotFoundError):
            raise hook_module._error

    # execute hook
    hook_func = getattr(hook_module, hook_type, None)
    if hook_func:
        _run_hook_function(obj, hook_type, hook_func, hook_source, key)


def _run_hook_function(
    obj: Settings,
    hook_type: str,
    hook_func: Callable,
    hook_source: str = "default",
    key: str = "",
):
    """
    Run a hook function:

    It execute @hook_func, update the results into settings @obj and
    add it to _loaded_hook registry ([@hook_source][@hook_type])
    """
    # optional settings argument
    try:
        hook_dict = hook_func(obj.dynaconf.clone())
    except TypeError:
        hook_dict = hook_func()

    # update obj settings
    if hook_dict:
        identifier = f"{hook_func.__name__}@{hook_source}"
        merge = hook_dict.pop(
            "dynaconf_merge", hook_dict.pop("DYNACONF_MERGE", False)
        )
        if key and key in hook_dict:
            obj.set(
                key,
                hook_dict[key],
                tomlfy=False,
                merge=merge,
                loader_identifier=identifier,
            )
        elif not key:
            obj.update(
                hook_dict,
                tomlfy=False,
                merge=merge,
                loader_identifier=identifier,
            )

    # add to registry
    obj._loaded_hooks[hook_source][hook_type] = hook_dict


def settings_loader(
    obj,
    settings_module=None,
    env=None,
    silent=True,
    key=None,
    filename=None,
    validate=False,
):
    """Loads from defined settings module

    :param obj: A dynaconf instance
    :param settings_module: A path or a list of paths e.g settings.toml
    :param env: Env to look for data defaults: development
    :param silent: Boolean to raise loading errors
    :param key: Load a single key if provided
    :param filename: optional filename to override the settings_module
    """
    if filename is None:
        settings_module = settings_module or obj.settings_module
        if not settings_module:  # pragma: no cover
            return
        files = ensure_a_list(settings_module)
    else:
        files = ensure_a_list(filename)

    files.extend(ensure_a_list(obj.get("SECRETS_FOR_DYNACONF", None)))

    found_files = []
    modules_names = []
    for item in files:
        item = str(item)  # Ensure str in case of LocalPath/Path is passed.
        p_root = obj._root_path or (
            os.path.dirname(found_files[0]) if found_files else None
        )
        if has_magic(item):
            # handle possible globs inside files list
            # like ["path/*.yaml", "path/ABC?.yaml"]
            globedfiles = glob(item, root_dir=p_root)
            for globedfile in globedfiles:
                # use object.find_file logic to handle skip files
                found = obj.find_file(globedfile, project_root=p_root)
                if found:
                    found_files.append(found)
        elif item.endswith(ct.ALL_EXTENSIONS + (".py",)):
            found = obj.find_file(item, project_root=p_root)
            if found:
                found_files.append(found)
        else:
            # a bare python module name w/o extension
            modules_names.append(item)

    enabled_core_loaders = [
        item.upper() for item in obj.get("CORE_LOADERS_FOR_DYNACONF") or []
    ]

    # add `.local.` to found_files list to search for local files.
    found_files.extend(
        [
            get_local_filename(item)
            for item in found_files
            if ".local." not in str(item)
        ]
    )

    for mod_file in modules_names + found_files:
        # can be set to multiple files settings.py,settings.yaml,...

        # Cascade all loaders
        loaders = [
            {"ext": ct.YAML_EXTENSIONS, "name": "YAML", "loader": yaml_loader},
            {"ext": ct.TOML_EXTENSIONS, "name": "TOML", "loader": toml_loader},
            {"ext": ct.INI_EXTENSIONS, "name": "INI", "loader": ini_loader},
            {"ext": ct.JSON_EXTENSIONS, "name": "JSON", "loader": json_loader},
        ]

        for loader in loaders:
            if loader["name"] not in enabled_core_loaders:
                continue

            if mod_file.endswith(loader["ext"]):
                loader["loader"].load(
                    obj,
                    filename=mod_file,
                    env=env,
                    silent=silent,
                    key=key,
                    validate=validate,
                )
                continue

        if mod_file.endswith(ct.ALL_EXTENSIONS):
            continue

        if "PY" not in enabled_core_loaders:
            # pyloader is disabled
            continue

        # must be Python file or module
        # load from default defined module settings.py or .secrets.py if exists
        py_loader.load(obj, mod_file, key=key, validate=validate)

        # load from the current env e.g: development_settings.py
        env = env or obj.current_env
        if mod_file.endswith(".py"):
            if ".secrets.py" == mod_file:
                tmpl = ".{0}_{1}{2}"
                mod_file = "secrets.py"
            else:
                tmpl = "{0}_{1}{2}"

            dirname = os.path.dirname(mod_file)
            filename, extension = os.path.splitext(os.path.basename(mod_file))
            new_filename = tmpl.format(env.lower(), filename, extension)
            env_mod_file = os.path.join(dirname, new_filename)
            global_filename = tmpl.format("global", filename, extension)
            global_mod_file = os.path.join(dirname, global_filename)
        else:
            env_mod_file = f"{env.lower()}_{mod_file}"
            global_mod_file = f"global_{mod_file}"

        py_loader.load(
            obj,
            env_mod_file,
            identifier=f"py_{env.upper()}",
            silent=True,
            key=key,
            validate=validate,
        )

        # load from global_settings.py
        py_loader.load(
            obj,
            global_mod_file,
            identifier="py_global",
            silent=True,
            key=key,
            validate=validate,
        )


def enable_external_loaders(obj):
    """Enable external service loaders like `VAULT_` and `REDIS_`
    looks forenv variables like `REDIS_ENABLED_FOR_DYNACONF`
    """
    for name, loader in ct.EXTERNAL_LOADERS.items():
        enabled = getattr(obj, f"{name.upper()}_ENABLED_FOR_DYNACONF", False)
        if (
            enabled
            and enabled not in false_values
            and loader not in obj.LOADERS_FOR_DYNACONF
        ):  # noqa
            obj.LOADERS_FOR_DYNACONF.insert(0, loader)


def write(filename, data, env=None, merge=False):
    """Writes `data` to `filename` infers format by file extension."""
    loader_name = f"{filename.rpartition('.')[-1]}_loader"
    loader = globals().get(loader_name)
    if not loader:
        raise OSError(f"{loader_name} cannot be found.")

    data = DynaBox(data, box_settings={}).to_dict()
    if loader is not py_loader and env and env not in data:
        data = {env: data}

    loader.write(filename, data, merge=merge)

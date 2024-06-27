from __future__ import annotations

import errno
import importlib
import inspect
import types
from contextlib import suppress
from pathlib import Path

from dynaconf import default_settings
from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils import DynaconfDict
from dynaconf.utils import object_merge
from dynaconf.utils import upperfy
from dynaconf.utils.files import find_file
from dynaconf.utils.functional import empty


def load(
    obj,
    settings_module,
    identifier="py",
    silent=False,
    key=None,
    validate=False,
):
    """
    Tries to import a python module

    Notes:
        It doesn't handle environment namespaces explicitly. Eg
            [default], [development], etc
        See tests/test_nested_loading.py sample python file
    """
    mod, loaded_from = get_module(obj, settings_module, silent)
    if not (mod and loaded_from):
        return

    # setup SourceMetadata (for inspecting)
    loader_identifier = SourceMetadata(identifier, mod.__name__, "global")

    load_from_python_object(
        obj, mod, settings_module, key, loader_identifier, validate=validate
    )


def load_from_python_object(
    obj, mod, settings_module, key=None, identifier=None, validate=False
):
    file_merge = getattr(mod, "dynaconf_merge", empty)
    if file_merge is empty:
        file_merge = getattr(mod, "DYNACONF_MERGE", empty)

    for setting in dir(mod):
        # A setting var in a Python file should start with upper case
        # valid: A_value=1, ABC_value=3 A_BBB__default=1
        # invalid: a_value=1, MyValue=3
        # This is to avoid loading functions, classes and built-ins
        if setting.split("__")[0].isupper():
            if key is None or key == setting:
                setting_value = getattr(mod, setting)
                obj.set(
                    setting,
                    setting_value,
                    loader_identifier=identifier,
                    merge=file_merge,
                    validate=validate,
                )

    obj._loaded_py_modules.append(mod.__name__)
    obj._loaded_files.append(mod.__file__)


def try_to_load_from_py_module_name(
    obj, name, key=None, identifier="py", silent=False, validate=False
):
    """Try to load module by its string name.

    Arguments:
        obj {LAzySettings} -- Dynaconf settings instance
        name {str} -- Name of the module e.g: foo.bar.zaz

    Keyword Arguments:
        key {str} -- Single key to be loaded (default: {None})
        identifier {str} -- Name of identifier to store (default: 'py')
        silent {bool} -- Weather to raise or silence exceptions.
    """
    ctx = suppress(ImportError, TypeError) if silent else suppress()

    # setup SourceMetadata (for inspecting)
    loader_identifier = SourceMetadata(identifier, name, "global")

    with ctx:
        mod = importlib.import_module(str(name))
        load_from_python_object(
            obj, mod, name, key, loader_identifier, validate=validate
        )
        return True  # loaded ok!
    # if it reaches this point that means exception occurred, module not found.
    return False


def get_module(obj, filename, silent=False):
    try:
        mod = importlib.import_module(filename)
        loaded_from = "module"
        mod.is_error = False
    except (ImportError, TypeError):
        mod = import_from_filename(obj, filename, silent=silent)
        if mod and not mod._is_error:
            loaded_from = "filename"
        else:
            # it is important to return None in case of not loaded
            loaded_from = None
    return mod, loaded_from


def import_from_filename(obj, filename, silent=False):  # pragma: no cover
    """If settings_module is a filename path import it."""
    if filename in [item.filename for item in inspect.stack()]:
        raise ImportError(
            "Looks like you are loading dynaconf "
            f"from inside the {filename} file and then it is trying "
            "to load itself entering in a circular reference "
            "problem. To solve it you have to "
            "invoke your program from another root folder "
            "or rename your program file."
        )

    _find_file = getattr(obj, "find_file", find_file)
    if not filename.endswith(".py"):
        filename = f"{filename}.py"

    if filename in default_settings.SETTINGS_FILE_FOR_DYNACONF:
        silent = True
    mod = types.ModuleType(filename.rstrip(".py"))
    mod.__file__ = filename
    mod._is_error = False
    mod._error = None
    try:
        with open(
            _find_file(filename),
            encoding=default_settings.ENCODING_FOR_DYNACONF,
        ) as config_file:
            exec(compile(config_file.read(), filename, "exec"), mod.__dict__)
    except OSError as e:
        e.strerror = (
            f"py_loader: error loading file " f"({e.strerror} {filename})\n"
        )
        if silent and e.errno in (errno.ENOENT, errno.EISDIR):
            return
        mod._is_error = True
        mod._error = e
    return mod


def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    """
    settings_path = Path(settings_path)
    if settings_path.exists() and merge:  # pragma: no cover
        existing = DynaconfDict()
        load(existing, str(settings_path))
        object_merge(existing, settings_data)
    with open(
        str(settings_path),
        "w",
        encoding=default_settings.ENCODING_FOR_DYNACONF,
    ) as f:
        f.writelines(
            [f"{upperfy(k)} = {repr(v)}\n" for k, v in settings_data.items()]
        )

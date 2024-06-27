from __future__ import annotations

from pathlib import Path

from dynaconf import default_settings
from dynaconf.constants import INI_EXTENSIONS
from dynaconf.loaders.base import BaseLoader
from dynaconf.utils import object_merge

try:
    from configobj import ConfigObj
except ImportError:  # pragma: no cover
    ConfigObj = None


def load(obj, env=None, silent=True, key=None, filename=None, validate=False):
    """
    Reads and loads in to "obj" a single key or all keys from source file.

    :param obj: the settings instance
    :param env: settings current env default='development'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all in env
    :param filename: Optional custom filename to load
    :return: None
    """
    if ConfigObj is None:  # pragma: no cover
        BaseLoader.warn_not_installed(obj, "ini")
        return

    loader = BaseLoader(
        obj=obj,
        env=env,
        identifier="ini",
        extensions=INI_EXTENSIONS,
        file_reader=lambda fileobj: ConfigObj(fileobj).dict(),
        string_reader=lambda strobj: ConfigObj(strobj.split("\n")).dict(),
        validate=validate,
    )
    loader.load(
        filename=filename,
        key=key,
        silent=silent,
    )


def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    """
    settings_path = Path(settings_path)
    if settings_path.exists() and merge:  # pragma: no cover
        with open(
            str(settings_path), encoding=default_settings.ENCODING_FOR_DYNACONF
        ) as open_file:
            object_merge(ConfigObj(open_file).dict(), settings_data)
    new = ConfigObj()
    new.update(settings_data)
    new.write(open(str(settings_path), "bw"))

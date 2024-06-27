from __future__ import annotations

import json
from pathlib import Path

from dynaconf import default_settings
from dynaconf.constants import JSON_EXTENSIONS
from dynaconf.loaders.base import BaseLoader
from dynaconf.utils import object_merge
from dynaconf.utils.parse_conf import try_to_encode

try:  # pragma: no cover
    import commentjson
except ImportError:  # pragma: no cover
    commentjson = None


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
    if (
        obj.get("COMMENTJSON_ENABLED_FOR_DYNACONF") and commentjson
    ):  # pragma: no cover  # noqa
        file_reader = commentjson.load
        string_reader = commentjson.loads
    else:
        file_reader = json.load
        string_reader = json.loads

    loader = BaseLoader(
        obj=obj,
        env=env,
        identifier="json",
        extensions=JSON_EXTENSIONS,
        file_reader=file_reader,
        string_reader=string_reader,
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
            object_merge(json.load(open_file), settings_data)

    with open(
        str(settings_path),
        "w",
        encoding=default_settings.ENCODING_FOR_DYNACONF,
    ) as open_file:
        json.dump(settings_data, open_file, cls=DynaconfEncoder)


class DynaconfEncoder(json.JSONEncoder):
    """Transform Dynaconf custom types instances to json representation"""

    def default(self, o):
        return try_to_encode(o, callback=super().default)

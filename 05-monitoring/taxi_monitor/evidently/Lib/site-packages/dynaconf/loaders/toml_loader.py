from __future__ import annotations

import warnings
from pathlib import Path

from dynaconf import default_settings
from dynaconf.constants import TOML_EXTENSIONS
from dynaconf.loaders.base import BaseLoader
from dynaconf.utils import object_merge
from dynaconf.vendor import toml  # Backwards compatibility with uiri/toml
from dynaconf.vendor import tomllib  # New tomllib stdlib on py3.11


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

    try:
        loader = BaseLoader(
            obj=obj,
            env=env,
            identifier="toml",
            extensions=TOML_EXTENSIONS,
            file_reader=tomllib.load,
            string_reader=tomllib.loads,
            opener_params={"mode": "rb"},
            validate=validate,
        )
        loader.load(
            filename=filename,
            key=key,
            silent=silent,
        )
    except UnicodeDecodeError:  # pragma: no cover
        """
        NOTE: Compat functions exists to keep backwards compatibility with
        the new tomllib library. The old library was called `toml` and
        the new one is called `tomllib`.

        The old lib uiri/toml allowed unicode characters and re-added files
        as string.

        The new tomllib (stdlib) does not allow unicode characters, only
        utf-8 encoded, and read files as binary.

        NOTE: In dynaconf 4.0.0 we will drop support for the old library
        removing the compat functions and calling directly the new lib.
        """
        loader = BaseLoader(
            obj=obj,
            env=env,
            identifier="toml",
            extensions=TOML_EXTENSIONS,
            file_reader=toml.load,
            string_reader=toml.loads,
            validate=validate,
        )
        loader.load(
            filename=filename,
            key=key,
            silent=silent,
        )

        warnings.warn(
            "TOML files should have only UTF-8 encoded characters. "
            "starting on 4.0.0 dynaconf will stop allowing invalid chars.",
        )


def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    """
    settings_path = Path(settings_path)
    if settings_path.exists() and merge:  # pragma: no cover
        try:  # tomllib first
            with open(str(settings_path), "rb") as open_file:
                object_merge(tomllib.load(open_file), settings_data)
        except UnicodeDecodeError:  # pragma: no cover
            # uiri/toml fallback (TBR on 4.0.0)
            with open(
                str(settings_path),
                encoding=default_settings.ENCODING_FOR_DYNACONF,
            ) as open_file:
                object_merge(toml.load(open_file), settings_data)

    try:  # tomllib first
        with open(str(settings_path), "wb") as open_file:
            tomllib.dump(encode_nulls(settings_data), open_file)
    except UnicodeEncodeError:  # pragma: no cover
        # uiri/toml fallback (TBR on 4.0.0)
        with open(
            str(settings_path),
            "w",
            encoding=default_settings.ENCODING_FOR_DYNACONF,
        ) as open_file:
            toml.dump(encode_nulls(settings_data), open_file)

        warnings.warn(
            "TOML files should have only UTF-8 encoded characters. "
            "starting on 4.0.0 dynaconf will stop allowing invalid chars.",
        )


def encode_nulls(data):
    """TOML does not support `None` so this function transforms to '@none '."""
    if data is None:
        return "@none "
    if isinstance(data, dict):
        return {key: encode_nulls(value) for key, value in data.items()}
    elif isinstance(data, (list, tuple)):
        return [encode_nulls(item) for item in data]
    return data

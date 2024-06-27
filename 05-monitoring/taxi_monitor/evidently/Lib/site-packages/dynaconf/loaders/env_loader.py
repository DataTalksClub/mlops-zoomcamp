from __future__ import annotations

from contextlib import suppress
from os import environ

from dynaconf.loaders.base import SourceMetadata
from dynaconf.utils import missing
from dynaconf.utils import upperfy
from dynaconf.utils.parse_conf import boolean_fix
from dynaconf.utils.parse_conf import parse_conf_data

DOTENV_IMPORTED = False
with suppress(ImportError, FileNotFoundError):
    from dynaconf.vendor.dotenv import cli as dotenv_cli

    DOTENV_IMPORTED = True

IDENTIFIER = "env"


def load(obj, env=None, silent=True, key=None, validate=False):
    """Loads envvars with prefixes:

    `DYNACONF_` (default global) or `$(ENVVAR_PREFIX_FOR_DYNACONF)_`
    """
    global_prefix = obj.get("ENVVAR_PREFIX_FOR_DYNACONF")
    if global_prefix is False or global_prefix.upper() != "DYNACONF":
        load_from_env(
            obj,
            "DYNACONF",
            key,
            silent,
            IDENTIFIER + "_global",
            validate=validate,
        )

    # Load the global env if exists and overwrite everything
    load_from_env(
        obj,
        global_prefix,
        key,
        silent,
        IDENTIFIER + "_global",
        validate=validate,
    )


def load_from_env(
    obj,
    prefix=False,
    key=None,
    silent=False,
    identifier=IDENTIFIER,
    env=False,  # backwards compatibility bc renamed param
    validate=False,
):
    if prefix is False and env is not False:
        prefix = env

    env_ = ""
    if prefix is not False:
        if not isinstance(prefix, str):
            raise TypeError("`prefix/env` must be str or False")

        prefix = prefix.upper()
        env_ = f"{prefix}_"

    # set source metadata
    source_metadata = SourceMetadata(identifier, "unique", "global")

    # Load a single environment variable explicitly.
    if key:
        key = upperfy(key)
        value = environ.get(f"{env_}{key}")
        if value:
            try:  # obj is a Settings
                obj.set(
                    key,
                    boolean_fix(value),
                    loader_identifier=source_metadata,
                    tomlfy=True,
                    validate=validate,
                )
            except AttributeError:  # obj is a dict
                obj[key] = parse_conf_data(
                    boolean_fix(value), tomlfy=True, box_settings=obj
                )

    # Load environment variables in bulk (when matching).
    else:
        # Only known variables should be loaded from environment?
        ignore_unknown = obj.get("IGNORE_UNKNOWN_ENVVARS_FOR_DYNACONF")

        # prepare data
        trim_len = len(env_)
        data = {
            key[trim_len:]: parse_conf_data(
                boolean_fix(value), tomlfy=True, box_settings=obj
            )
            for key, value in environ.items()
            if key.startswith(env_)
            and not (
                # Ignore environment variables that haven't been
                # pre-defined in settings space.
                ignore_unknown
                and obj.get(key[trim_len:], default=missing) is missing
            )
        }
        # Update the settings space based on gathered data from environment.
        if data:
            filter_strategy = obj.get("FILTER_STRATEGY")
            if filter_strategy:
                data = filter_strategy(data)
            obj.update(
                data, loader_identifier=source_metadata, validate=validate
            )


def write(settings_path, settings_data, **kwargs):
    """Write data to .env file"""
    if not DOTENV_IMPORTED:  # pragma: no cover
        return
    for key, value in settings_data.items():
        quote_mode = (
            isinstance(value, str)
            and (value.startswith("'") or value.startswith('"'))
        ) or isinstance(value, (list, dict))
        dotenv_cli.set_key(
            str(settings_path),
            key,
            str(value),
            quote_mode="always" if quote_mode else "none",
        )

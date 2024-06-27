from __future__ import annotations

import importlib
import os
import sys
import warnings

from dynaconf.utils import RENAMED_VARS
from dynaconf.utils import upperfy
from dynaconf.utils import warn_deprecations
from dynaconf.utils.files import find_file
from dynaconf.utils.parse_conf import boolean_fix
from dynaconf.utils.parse_conf import parse_conf_data
from dynaconf.vendor.dotenv import load_dotenv


def try_renamed(key, value, older_key, current_key):
    if value is None:
        if key == current_key:
            if older_key in os.environ:
                warnings.warn(
                    f"{older_key} is deprecated please use {current_key}",
                    DeprecationWarning,
                )
                value = os.environ[older_key]
    return value


def get(key, default=None):
    value = os.environ.get(upperfy(key))

    # compatibility with renamed variables
    for old, new in RENAMED_VARS.items():
        value = try_renamed(key, value, old, new)

    return (
        parse_conf_data(boolean_fix(value), tomlfy=True, box_settings={})
        if value is not None
        else default
    )


def start_dotenv(obj=None, root_path=None):
    # load_from_dotenv_if_installed
    obj = obj or {}
    _find_file = getattr(obj, "find_file", find_file)
    root_path = (
        root_path
        or getattr(obj, "_root_path", None)
        or get("ROOT_PATH_FOR_DYNACONF")
    )

    dotenv_path = (
        obj.get("DOTENV_PATH_FOR_DYNACONF")
        or get("DOTENV_PATH_FOR_DYNACONF")
        or _find_file(".env", project_root=root_path)
    )

    load_dotenv(
        dotenv_path,
        verbose=obj.get("DOTENV_VERBOSE_FOR_DYNACONF", False),
        override=obj.get("DOTENV_OVERRIDE_FOR_DYNACONF", False),
    )

    warn_deprecations(os.environ)


def reload(load_dotenv=None, *args, **kwargs):
    if load_dotenv:
        start_dotenv(*args, **kwargs)
    importlib.reload(sys.modules[__name__])


# default proj root
# pragma: no cover
ROOT_PATH_FOR_DYNACONF = get("ROOT_PATH_FOR_DYNACONF", None)

# Default settings file
SETTINGS_FILE_FOR_DYNACONF = get("SETTINGS_FILE_FOR_DYNACONF", [])

# MISSPELLS `FILES` when/if it happens
misspelled_files = get("SETTINGS_FILES_FOR_DYNACONF", None)
if not SETTINGS_FILE_FOR_DYNACONF and misspelled_files is not None:
    SETTINGS_FILE_FOR_DYNACONF = misspelled_files

# # ENV SETTINGS
# # In dynaconf 1.0.0 `NAMESPACE` got renamed to `ENV`


# If provided environments will be loaded separately
ENVIRONMENTS_FOR_DYNACONF = get("ENVIRONMENTS_FOR_DYNACONF", False)
MAIN_ENV_FOR_DYNACONF = get("MAIN_ENV_FOR_DYNACONF", "MAIN")

# If False dynaconf will allow access to first level settings only in upper
LOWERCASE_READ_FOR_DYNACONF = get("LOWERCASE_READ_FOR_DYNACONF", True)

# The environment variable to switch current env
ENV_SWITCHER_FOR_DYNACONF = get(
    "ENV_SWITCHER_FOR_DYNACONF", "ENV_FOR_DYNACONF"
)

# The current env by default is DEVELOPMENT
# to switch is needed to `export ENV_FOR_DYNACONF=PRODUCTION`
# or put that value in .env file
# this value is used only when reading files like .toml|yaml|ini|json
ENV_FOR_DYNACONF = get(ENV_SWITCHER_FOR_DYNACONF, "DEVELOPMENT")

# This variable exists to support `from_env` method
FORCE_ENV_FOR_DYNACONF = get("FORCE_ENV_FOR_DYNACONF", None)

# Default values is taken from DEFAULT pseudo env
# this value is used only when reading files like .toml|yaml|ini|json
DEFAULT_ENV_FOR_DYNACONF = get("DEFAULT_ENV_FOR_DYNACONF", "DEFAULT")

# Global values are taken from DYNACONF env used for exported envvars
# Values here overwrites all other envs
# This namespace is used for files and also envvars
ENVVAR_PREFIX_FOR_DYNACONF = get("ENVVAR_PREFIX_FOR_DYNACONF", "DYNACONF")

# By default all environment variables (filtered by `envvar_prefix`) will
# be pulled into settings space. In case some of them are polluting the space,
# setting this flag to `True` will change this behaviour.
# Only "known" variables will be considered -- that is variables defined before
# in settings files (or includes/preloads).
IGNORE_UNKNOWN_ENVVARS_FOR_DYNACONF = get(
    "IGNORE_UNKNOWN_ENVVARS_FOR_DYNACONF", False
)

AUTO_CAST_FOR_DYNACONF = get("AUTO_CAST_FOR_DYNACONF", True)

# The default encoding to open settings files
ENCODING_FOR_DYNACONF = get("ENCODING_FOR_DYNACONF", "utf-8")

# Merge objects on load
MERGE_ENABLED_FOR_DYNACONF = get("MERGE_ENABLED_FOR_DYNACONF", False)

# Lookup keys considering dots as separators
DOTTED_LOOKUP_FOR_DYNACONF = get("DOTTED_LOOKUP_FOR_DYNACONF", True)

# BY default `__` is the separator for nested env vars
# export `DYNACONF__DATABASE__server=server.com`
# export `DYNACONF__DATABASE__PORT=6666`
# Should result in settings.DATABASE == {'server': 'server.com', 'PORT': 6666}
# To disable it one can set `NESTED_SEPARATOR_FOR_DYNACONF=false`
NESTED_SEPARATOR_FOR_DYNACONF = get("NESTED_SEPARATOR_FOR_DYNACONF", "__")

# The env var specifying settings module
ENVVAR_FOR_DYNACONF = get("ENVVAR_FOR_DYNACONF", "SETTINGS_FILE_FOR_DYNACONF")

# Default values for redis configs
default_redis = {
    "host": get("REDIS_HOST_FOR_DYNACONF", "localhost"),
    "port": int(get("REDIS_PORT_FOR_DYNACONF", 6379)),
    "db": int(get("REDIS_DB_FOR_DYNACONF", 0)),
    "decode_responses": get("REDIS_DECODE_FOR_DYNACONF", True),
    "username": get("REDIS_USERNAME_FOR_DYNACONF", None),
    "password": get("REDIS_PASSWORD_FOR_DYNACONF", None),
}
REDIS_FOR_DYNACONF = get("REDIS_FOR_DYNACONF", default_redis)
REDIS_ENABLED_FOR_DYNACONF = get("REDIS_ENABLED_FOR_DYNACONF", False)

# Hashicorp Vault Project
vault_scheme = get("VAULT_SCHEME_FOR_DYNACONF", "http")
vault_host = get("VAULT_HOST_FOR_DYNACONF", "localhost")
vault_port = get("VAULT_PORT_FOR_DYNACONF", "8200")
default_vault = {
    "url": get(
        "VAULT_URL_FOR_DYNACONF", f"{vault_scheme}://{vault_host}:{vault_port}"
    ),
    "token": get("VAULT_TOKEN_FOR_DYNACONF", None),
    "cert": get("VAULT_CERT_FOR_DYNACONF", None),
    "verify": get("VAULT_VERIFY_FOR_DYNACONF", None),
    "timeout": get("VAULT_TIMEOUT_FOR_DYNACONF", None),
    "proxies": get("VAULT_PROXIES_FOR_DYNACONF", None),
    "allow_redirects": get("VAULT_ALLOW_REDIRECTS_FOR_DYNACONF", None),
    "namespace": get("VAULT_NAMESPACE_FOR_DYNACONF", None),
}
VAULT_FOR_DYNACONF = get("VAULT_FOR_DYNACONF", default_vault)
VAULT_ENABLED_FOR_DYNACONF = get("VAULT_ENABLED_FOR_DYNACONF", False)
VAULT_PATH_FOR_DYNACONF = get("VAULT_PATH_FOR_DYNACONF", "dynaconf")
VAULT_MOUNT_POINT_FOR_DYNACONF = get(
    "VAULT_MOUNT_POINT_FOR_DYNACONF", "secret"
)
VAULT_ROOT_TOKEN_FOR_DYNACONF = get("VAULT_ROOT_TOKEN_FOR_DYNACONF", None)
VAULT_KV_VERSION_FOR_DYNACONF = get("VAULT_KV_VERSION_FOR_DYNACONF", 1)
VAULT_AUTH_WITH_IAM_FOR_DYNACONF = get(
    "VAULT_AUTH_WITH_IAM_FOR_DYNACONF", False
)
VAULT_AUTH_ROLE_FOR_DYNACONF = get("VAULT_AUTH_ROLE_FOR_DYNACONF", None)
VAULT_ROLE_ID_FOR_DYNACONF = get("VAULT_ROLE_ID_FOR_DYNACONF", None)
VAULT_SECRET_ID_FOR_DYNACONF = get("VAULT_SECRET_ID_FOR_DYNACONF", None)
VAULT_USERNAME_FOR_DYNACONF = get("VAULT_USERNAME_FOR_DYNACONF", None)
VAULT_PASSWORD_FOR_DYNACONF = get("VAULT_PASSWORD_FOR_DYNACONF", None)

# Only core loaders defined on this list will be invoked
core_loaders = ["YAML", "TOML", "INI", "JSON", "PY"]
CORE_LOADERS_FOR_DYNACONF = get("CORE_LOADERS_FOR_DYNACONF", core_loaders)

# External Loaders to read vars from different data stores
default_loaders = [
    "dynaconf.loaders.env_loader",
    # 'dynaconf.loaders.redis_loader'
    # 'dynaconf.loaders.vault_loader'
]
LOADERS_FOR_DYNACONF = get("LOADERS_FOR_DYNACONF", default_loaders)

# Errors in loaders should be silenced?
SILENT_ERRORS_FOR_DYNACONF = get("SILENT_ERRORS_FOR_DYNACONF", True)

# always fresh variables
FRESH_VARS_FOR_DYNACONF = get("FRESH_VARS_FOR_DYNACONF", [])

DOTENV_PATH_FOR_DYNACONF = get("DOTENV_PATH_FOR_DYNACONF", None)
DOTENV_VERBOSE_FOR_DYNACONF = get("DOTENV_VERBOSE_FOR_DYNACONF", False)
DOTENV_OVERRIDE_FOR_DYNACONF = get("DOTENV_OVERRIDE_FOR_DYNACONF", False)

# Currently this is only used by cli. INSTANCE_FOR_DYNACONF specifies python
# dotted path to custom LazySettings instance. Last dotted path item should be
# instance of LazySettings.
INSTANCE_FOR_DYNACONF = get("INSTANCE_FOR_DYNACONF", None)

# https://msg.pyyaml.org/load
YAML_LOADER_FOR_DYNACONF = get("YAML_LOADER_FOR_DYNACONF", "safe_load")

# Use commentjson? https://commentjson.readthedocs.io/en/latest/
COMMENTJSON_ENABLED_FOR_DYNACONF = get(
    "COMMENTJSON_ENABLED_FOR_DYNACONF", False
)

# Extra file, or list of files where to look for secrets
# useful for CI environment like jenkins
# where you can export this variable pointing to a local
# absolute path of the secrets file.
SECRETS_FOR_DYNACONF = get("SECRETS_FOR_DYNACONF", None)

# To include extra paths based on envvar
INCLUDES_FOR_DYNACONF = get("INCLUDES_FOR_DYNACONF", [])

# To pre-load extra paths based on envvar
PRELOAD_FOR_DYNACONF = get("PRELOAD_FOR_DYNACONF", [])

# Files to skip if found on search tree
SKIP_FILES_FOR_DYNACONF = get("SKIP_FILES_FOR_DYNACONF", [])

# YAML reads empty vars as None, should dynaconf apply validator defaults?
# this is set to None, then evaluated on base.Settings.setdefault
# possible values are True/False
APPLY_DEFAULT_ON_NONE_FOR_DYNACONF = get(
    "APPLY_DEFAULT_ON_NONE_FOR_DYNACONF", None
)

# Auto trigger validation when Settings update methods are called directly
# (set, update, load_file)
VALIDATE_ON_UPDATE_FOR_DYNACONF = get("VALIDATE_ON_UPDATE_FOR_DYNACONF", False)

# Use system environ as fallback when a setting was not set
SYSENV_FALLBACK_FOR_DYNACONF = get("SYSENV_FALLBACK_FOR_DYNACONF", False)


# Backwards compatibility with renamed variables
for old, new in RENAMED_VARS.items():
    setattr(sys.modules[__name__], old, locals()[new])

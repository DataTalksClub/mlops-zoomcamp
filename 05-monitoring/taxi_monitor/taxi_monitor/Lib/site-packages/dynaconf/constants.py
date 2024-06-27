# pragma: no cover
from __future__ import annotations

INI_EXTENSIONS = (".ini", ".conf", ".properties")
TOML_EXTENSIONS = (".toml", ".tml")
YAML_EXTENSIONS = (".yaml", ".yml")
JSON_EXTENSIONS = (".json",)

ALL_EXTENSIONS = (
    INI_EXTENSIONS + TOML_EXTENSIONS + YAML_EXTENSIONS + JSON_EXTENSIONS
)  # noqa

EXTERNAL_LOADERS = {
    "ENV": "dynaconf.loaders.env_loader",
    "VAULT": "dynaconf.loaders.vault_loader",
    "REDIS": "dynaconf.loaders.redis_loader",
}

DJANGO_PATCH = """
# HERE STARTS DYNACONF EXTENSION LOAD (Keep at the very bottom of settings.py)
# Read more at https://www.dynaconf.com/django/
import dynaconf  # noqa
settings = dynaconf.DjangoDynaconf(__name__)  # noqa
# HERE ENDS DYNACONF EXTENSION LOAD (No more code below this line)
 """

INSTANCE_TEMPLATE = """
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files={settings_files},
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
"""

EXTS = (
    "py",
    "toml",
    "tml",
    "yaml",
    "yml",
    "ini",
    "conf",
    "properties",
    "json",
)
DEFAULT_SETTINGS_FILES = [f"settings.{ext}" for ext in EXTS] + [
    f".secrets.{ext}" for ext in EXTS
]

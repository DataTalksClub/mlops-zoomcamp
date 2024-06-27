from __future__ import annotations

from dynaconf.base import LazySettings
from dynaconf.constants import DEFAULT_SETTINGS_FILES
from dynaconf.contrib import DjangoDynaconf
from dynaconf.contrib import FlaskDynaconf
from dynaconf.utils.inspect import get_history
from dynaconf.utils.inspect import inspect_settings
from dynaconf.utils.parse_conf import add_converter
from dynaconf.utils.parse_conf import DynaconfFormatError
from dynaconf.utils.parse_conf import DynaconfParseError
from dynaconf.validator import ValidationError
from dynaconf.validator import Validator

settings = LazySettings(
    # This global `settings` is deprecated from v3.0.0+
    # kept here for backwards compatibility
    # To Be Removed in 4.0.x
    warn_dynaconf_global_settings=True,
    environments=True,
    lowercase_read=False,
    load_dotenv=True,
    default_settings_paths=DEFAULT_SETTINGS_FILES,
)


# This is the new recommended base class alias
Dynaconf = LazySettings  # noqa

__all__ = [
    "Dynaconf",
    "LazySettings",
    "Validator",
    "FlaskDynaconf",
    "ValidationError",
    "DjangoDynaconf",
    "add_converter",
    "inspect_settings",
    "get_history",
    "DynaconfFormatError",
    "DynaconfParseError",
]

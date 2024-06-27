from __future__ import annotations

import inspect
from functools import wraps

from dynaconf.utils import find_the_correct_casing
from dynaconf.utils import recursively_evaluate_lazy_format
from dynaconf.utils.functional import empty
from dynaconf.vendor.box import Box


def evaluate_lazy_format(f):
    """Marks a method on Dynabox instance to
    lazily evaluate LazyFormat objects upon access."""

    @wraps(f)
    def evaluate(dynabox, item, *args, **kwargs):
        value = f(dynabox, item, *args, **kwargs)
        settings = dynabox._box_config["box_settings"]

        if getattr(value, "_dynaconf_lazy_format", None):
            dynabox._box_config[f"raw_{item.lower()}"] = (
                f"@{value.formatter.token} {value.value}"
            )

        return recursively_evaluate_lazy_format(value, settings)

    return evaluate


class DynaBox(Box):
    """Specialized Box for dynaconf
    it allows items/attrs to be found both in upper or lower case"""

    @evaluate_lazy_format
    def __getattr__(self, item, *args, **kwargs):
        try:
            return super().__getattr__(item, *args, **kwargs)
        except (AttributeError, KeyError):
            n_item = find_the_correct_casing(item, self) or item
            return super().__getattr__(n_item, *args, **kwargs)

    @evaluate_lazy_format
    def __getitem__(self, item, *args, **kwargs):
        try:
            return super().__getitem__(item, *args, **kwargs)
        except (AttributeError, KeyError):
            n_item = find_the_correct_casing(item, self) or item
            return super().__getitem__(n_item, *args, **kwargs)

    def _safe_get(self, item, *args, **kwargs):
        """Get item bypassing recursive evaluation"""
        try:
            return super().__getitem__(item, *args, **kwargs)
        except (AttributeError, KeyError):
            n_item = find_the_correct_casing(item, self) or item
            return super().__getitem__(n_item, *args, **kwargs)

    def __copy__(self):
        return self.__class__(
            super(Box, self).copy(),
            box_settings=self._box_config.get("box_settings"),
        )

    def copy(self):
        return self.__class__(
            super(Box, self).copy(),
            box_settings=self._box_config.get("box_settings"),
        )

    @evaluate_lazy_format
    def get(self, item, default=None, *args, **kwargs):
        n_item = find_the_correct_casing(item, self) or item
        value = super().get(n_item, empty, *args, **kwargs)
        return value if value is not empty else default

    def __dir__(self):
        keys = list(self.keys())
        reserved = [
            item[0]
            for item in inspect.getmembers(DynaBox)
            if not item[0].startswith("__")
        ]
        return (
            keys
            + [k.lower() for k in keys]
            + [k.upper() for k in keys]
            + reserved
        )

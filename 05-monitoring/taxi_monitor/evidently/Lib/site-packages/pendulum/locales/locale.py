from __future__ import annotations

import re

from importlib import import_module
from pathlib import Path
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import cast

from pendulum.utils._compat import resources


class Locale:
    """
    Represent a specific locale.
    """

    _cache: ClassVar[dict[str, Locale]] = {}

    def __init__(self, locale: str, data: Any) -> None:
        self._locale: str = locale
        self._data: Any = data
        self._key_cache: dict[str, str] = {}

    @classmethod
    def load(cls, locale: str | Locale) -> Locale:
        if isinstance(locale, Locale):
            return locale

        locale = cls.normalize_locale(locale)
        if locale in cls._cache:
            return cls._cache[locale]

        # Checking locale existence
        actual_locale = locale
        locale_path = cast(Path, resources.files(__package__).joinpath(actual_locale))
        while not locale_path.exists():
            if actual_locale == locale:
                raise ValueError(f"Locale [{locale}] does not exist.")

            actual_locale = actual_locale.split("_")[0]

        m = import_module(f"pendulum.locales.{actual_locale}.locale")

        cls._cache[locale] = cls(locale, m.locale)

        return cls._cache[locale]

    @classmethod
    def normalize_locale(cls, locale: str) -> str:
        m = re.match("([a-z]{2})[-_]([a-z]{2})", locale, re.I)
        if m:
            return f"{m.group(1).lower()}_{m.group(2).lower()}"
        else:
            return locale.lower()

    def get(self, key: str, default: Any | None = None) -> Any:
        if key in self._key_cache:
            return self._key_cache[key]

        parts = key.split(".")
        try:
            result = self._data[parts[0]]
            for part in parts[1:]:
                result = result[part]
        except KeyError:
            result = default

        self._key_cache[key] = result

        return self._key_cache[key]

    def translation(self, key: str) -> Any:
        return self.get(f"translations.{key}")

    def plural(self, number: int) -> str:
        return cast(str, self._data["plural"](number))

    def ordinal(self, number: int) -> str:
        return cast(str, self._data["ordinal"](number))

    def ordinalize(self, number: int) -> str:
        ordinal = self.get(f"custom.ordinal.{self.ordinal(number)}")

        if not ordinal:
            return f"{number}"

        return f"{number}{ordinal}"

    def match_translation(self, key: str, value: Any) -> dict[str, str] | None:
        translations = self.translation(key)
        if value not in translations.values():
            return None

        return cast(Dict[str, str], {v: k for k, v in translations.items()}[value])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self._locale}')"

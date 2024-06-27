from __future__ import annotations

from pendulum.formatting import Formatter


_formatter = Formatter()


class FormattableMixin:
    _formatter: Formatter = _formatter

    def format(self, fmt: str, locale: str | None = None) -> str:
        """
        Formats the instance using the given format.

        :param fmt: The format to use
        :param locale: The locale to use
        """
        return self._formatter.format(self, fmt, locale)

    def for_json(self) -> str:
        """
        Methods for automatic json serialization by simplejson.
        """
        return self.isoformat()

    def __format__(self, format_spec: str) -> str:
        if len(format_spec) > 0:
            if "%" in format_spec:
                return self.strftime(format_spec)

            return self.format(format_spec)

        return str(self)

    def __str__(self) -> str:
        return self.isoformat()

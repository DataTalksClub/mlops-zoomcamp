from ..formatting import Formatter


_formatter = Formatter()


class FormattableMixin(object):

    _formatter = _formatter

    def format(self, fmt, locale=None):
        """
        Formats the instance using the given format.

        :param fmt: The format to use
        :type fmt: str

        :param locale: The locale to use
        :type locale: str or None

        :rtype: str
        """
        return self._formatter.format(self, fmt, locale)

    def for_json(self):
        """
        Methods for automatic json serialization by simplejson

        :rtype: str
        """
        return str(self)

    def __format__(self, format_spec):
        if len(format_spec) > 0:
            if "%" in format_spec:
                return self.strftime(format_spec)

            return self.format(format_spec)

        return str(self)

    def __str__(self):
        return self.isoformat()

from __future__ import annotations

from dynaconf.utils import upperfy


class PrefixFilter:
    """Filter environment variables by prefix.

    Examples:
        Please see [Prefix filtering][prefix-filtering] in the advanced usage
        section.
    """

    def __init__(self, prefix: str):
        """Initialises the PrefixFilter class.

        Args:
            prefix: The prefix to filter on.
        """
        if not isinstance(prefix, str):
            raise TypeError("`SETTINGS_FILE_PREFIX` must be str")
        self.prefix = f"{upperfy(prefix)}_"

    def __call__(self, data):
        """Filter incoming data by prefix."""
        len_prefix = len(self.prefix)
        return {
            upperfy(key[len_prefix:]): value
            for key, value in data.items()
            if upperfy(key[:len_prefix]) == self.prefix
        }

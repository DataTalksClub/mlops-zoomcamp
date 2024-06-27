from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union

__all__ = (
    "SecretBytes",
    "SecretString",
    "SecretT",
    "SecretValue",
)

# NOTE: Union instead of ` | ` is used for compatibility with Sphinx autodoc.
#  - Sphinx autodoc doesn't handle string annotations for "bound" parameter in TypeVar.
#  - We cannot use `|` without string annotations due to supporting < python 3.10.
SecretT = TypeVar("SecretT", bound=Union[str, bytes])
"""Type that represents a secret value of type ``str`` or ``bytes``."""


class SecretValue(ABC, Generic[SecretT]):
    """Represents a secret value that can be of type `str` or `bytes`."""

    def __init__(self, secret_value: SecretT) -> None:
        """Initializes a :class:`SecretValue` object with a secret value of type ``str`` or ``bytes``.

        Args:
            secret_value (str | bytes): The secret value to be encapsulated.
        """

        self._secret_value = secret_value

    def get_secret(self) -> SecretT:
        """Returns the actual secret value.

        Returns:
            str | bytes: The secret value.
        """

        return self._secret_value

    @abstractmethod
    def get_obscured(self) -> SecretT:
        """Return the hidden representation of the secret value.

        Raises:
            NotImplementedError: Always raised to enforce implementation in subclasses.
        """

        raise NotImplementedError("Subclasses must implement get_obscured")

    def __str__(self) -> str:
        """Returns a string representation of the hidden secret value.

        Returns:
            str: String representation of the hidden secret value.
        """

        return str(self.get_obscured())

    def __repr__(self) -> str:
        """Returns a string representation of the object for debugging purposes.

        Returns:
            str: String representation of the object.
        """

        class_name = self.__class__.__name__
        return f"{class_name}({self.get_obscured()!r})"


class SecretString(SecretValue[str]):
    """Represents a secret string value."""

    def get_obscured(self) -> str:
        """Overrides the base class method to return the hidden string value.

        Returns:
            str: The hidden string representation of the secret value.
        """

        return "******"


class SecretBytes(SecretValue[bytes]):
    """Represents a secret bytes value."""

    def get_obscured(self) -> bytes:
        """Overrides the base class method to return the hidden bytes value.

        Returns:
            bytes: The hidden bytes representation of the secret value.
        """

        return b"******"

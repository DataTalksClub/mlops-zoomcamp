from __future__ import annotations

from typing import Any, ClassVar, Collection, Iterable, Protocol, TypeVar, runtime_checkable

__all__ = (
    "DataclassProtocol",
    "InstantiableCollection",
    "Logger",
)


class Logger(Protocol):
    """Logger protocol."""

    def debug(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Output a log message at 'DEBUG' level.

        Args:
             event: Log message.
             *args: Any args.
             **kwargs: Any kwargs.
        """

    def info(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Output a log message at 'INFO' level.

        Args:
             event: Log message.
             *args: Any args.
             **kwargs: Any kwargs.
        """

    def warning(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Output a log message at 'WARNING' level.

        Args:
             event: Log message.
             *args: Any args.
             **kwargs: Any kwargs.
        """

    def warn(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Output a log message at 'WARN' level.

        Args:
             event: Log message.
             *args: Any args.
             **kwargs: Any kwargs.
        """

    def error(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Output a log message at 'ERROR' level.

        Args:
             event: Log message.
             *args: Any args.
             **kwargs: Any kwargs.
        """

    def fatal(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Output a log message at 'FATAL' level.

        Args:
             event: Log message.
             *args: Any args.
             **kwargs: Any kwargs.
        """

    def exception(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Log a message with level 'ERROR' on this logger. The arguments are interpreted as for debug(). Exception info
        is added to the logging message.

        Args:
             event: Log message.
             *args: Any args.
             **kwargs: Any kwargs.
        """

    def critical(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Output a log message at 'INFO' level.

        Args:
             event: Log message.
             *args: Any args.
             **kwargs: Any kwargs.
        """

    def setLevel(self, level: int) -> None:  # noqa: N802
        """Set the log level

        Args:
            level: Log level to set as an integer

        Returns:
            None
        """


@runtime_checkable
class DataclassProtocol(Protocol):
    """Protocol for instance checking dataclasses"""

    __dataclass_fields__: ClassVar[dict[str, Any]]


T_co = TypeVar("T_co", covariant=True)


@runtime_checkable
class InstantiableCollection(Collection[T_co], Protocol[T_co]):  # pyright: ignore
    """A protocol for instantiable collection types."""

    def __init__(self, iterable: Iterable[T_co], /) -> None: ...

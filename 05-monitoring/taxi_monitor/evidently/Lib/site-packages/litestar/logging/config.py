from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from importlib.util import find_spec
from logging import INFO
from typing import TYPE_CHECKING, Any, Callable, Literal, cast

from litestar.exceptions import ImproperlyConfiguredException, MissingDependencyException
from litestar.serialization.msgspec_hooks import _msgspec_json_encoder
from litestar.utils.dataclass import simple_asdict
from litestar.utils.deprecation import deprecated, warn_deprecation

__all__ = ("BaseLoggingConfig", "LoggingConfig", "StructLoggingConfig")


if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import NoReturn

    # these imports are duplicated on purpose so sphinx autodoc can find and link them
    from structlog.types import BindableLogger, Processor, WrappedLogger
    from structlog.typing import EventDict

    from litestar.types import Logger, Scope
    from litestar.types.callable_types import ExceptionLoggingHandler, GetLogger


default_handlers: dict[str, dict[str, Any]] = {
    "console": {
        "class": "logging.StreamHandler",
        "level": "DEBUG",
        "formatter": "standard",
    },
    "queue_listener": {
        "class": "litestar.logging.standard.QueueListenerHandler",
        "level": "DEBUG",
        "formatter": "standard",
    },
}

if sys.version_info >= (3, 12, 0):
    default_handlers["queue_listener"].update(
        {
            "class": "logging.handlers.QueueHandler",
            "queue": {
                "()": "queue.Queue",
                "maxsize": -1,
            },
            "listener": "litestar.logging.standard.LoggingQueueListener",
            "handlers": ["console"],
        }
    )

    # do not format twice, the console handler will do the job
    del default_handlers["queue_listener"]["formatter"]


default_picologging_handlers: dict[str, dict[str, Any]] = {
    "console": {
        "class": "picologging.StreamHandler",
        "level": "DEBUG",
        "formatter": "standard",
    },
    "queue_listener": {
        "class": "litestar.logging.picologging.QueueListenerHandler",
        "level": "DEBUG",
        "formatter": "standard",
    },
}


def _get_default_formatters() -> dict[str, dict[str, Any]]:
    return {
        "standard": {"format": "%(levelname)s - %(asctime)s - %(name)s - %(module)s - %(message)s"},
    }


def _get_default_loggers() -> dict[str, dict[str, Any]]:
    return {
        "litestar": {"level": "INFO", "handlers": ["queue_listener"], "propagate": False},
    }


def get_logger_placeholder(_: str | None = None) -> NoReturn:
    """Raise: An :class:`ImproperlyConfiguredException <.exceptions.ImproperlyConfiguredException>`"""
    raise ImproperlyConfiguredException(
        "cannot call '.get_logger' without passing 'logging_config' to the Litestar constructor first"
    )


def _get_default_handlers() -> dict[str, dict[str, Any]]:
    """Return the default logging handlers for the config.

    Returns:
        A dictionary of logging handlers
    """
    if find_spec("picologging"):
        return default_picologging_handlers
    return default_handlers


def _default_exception_logging_handler_factory(
    is_struct_logger: bool,
    traceback_line_limit: int,
) -> ExceptionLoggingHandler:
    """Create an exception logging handler function.

    Args:
        is_struct_logger: Whether the logger is a structlog instance.
        traceback_line_limit: Maximal number of lines to log from the
            traceback. This parameter is deprecated and ignored.

    Returns:
        An exception logging handler.
    """

    if traceback_line_limit != -1:
        warn_deprecation(
            version="2.9.0",
            deprecated_name="traceback_line_limit",
            kind="parameter",
            info="The value is ignored. Use a custom 'exception_logging_handler' instead.",
            removal_in="3.0",
        )

    if is_struct_logger:

        def _default_exception_logging_handler(logger: Logger, scope: Scope, tb: list[str]) -> None:
            logger.exception(
                "Uncaught exception",
                connection_type=scope["type"],
                path=scope["path"],
            )

    else:

        def _default_exception_logging_handler(logger: Logger, scope: Scope, tb: list[str]) -> None:
            logger.exception(
                "Uncaught exception (connection_type=%s, path=%s):",
                scope["type"],
                scope["path"],
            )

    return _default_exception_logging_handler


class BaseLoggingConfig(ABC):
    """Abstract class that should be extended by logging configs."""

    __slots__ = ("log_exceptions", "traceback_line_limit", "exception_logging_handler")

    log_exceptions: Literal["always", "debug", "never"]
    """Should exceptions be logged, defaults to log exceptions when ``app.debug == True``'"""
    traceback_line_limit: int
    """Max number of lines to print for exception traceback.

    .. deprecated:: 2.9.0
        This parameter is deprecated and ignored. It will be removed in a future release.
    """
    exception_logging_handler: ExceptionLoggingHandler | None
    """Handler function for logging exceptions."""

    @abstractmethod
    def configure(self) -> GetLogger:
        """Return logger with the given configuration.

        Returns:
            A 'logging.getLogger' like function.
        """
        raise NotImplementedError("abstract method")

    @staticmethod
    def set_level(logger: Any, level: int) -> None:
        """Provides a consistent interface to call `setLevel` for all loggers."""
        raise NotImplementedError("abstract method")


@dataclass
class LoggingConfig(BaseLoggingConfig):
    """Configuration class for standard logging.

    Notes:
        - If 'picologging' is installed it will be used by default.
    """

    version: Literal[1] = field(default=1)
    """The only valid value at present is 1."""
    incremental: bool = field(default=False)
    """Whether the configuration is to be interpreted as incremental to the existing configuration.

    Notes:
        - This option is ignored for 'picologging'
    """
    disable_existing_loggers: bool = field(default=False)
    """Whether any existing non-root loggers are to be disabled."""
    filters: dict[str, dict[str, Any]] | None = field(default=None)
    """A dict in which each key is a filter id and each value is a dict describing how to configure the
    corresponding Filter_ instance.

    .. _Filter: https://docs.python.org/3/library/logging.html#filter-objects
    """
    propagate: bool = field(default=True)
    """If messages must propagate to handlers higher up the logger hierarchy from this logger.

    .. deprecated:: 2.10.0
        This parameter is deprecated. It will be removed in a future release. Use ``propagate`` at the logger level.
    """
    formatters: dict[str, dict[str, Any]] = field(default_factory=_get_default_formatters)
    """A dict in which each key is a formatter and each value is a dict describing how to configure the
    corresponding Formatter_ instance. A ``standard`` formatter is provided.

    .. _Formatter: https://docs.python.org/3/library/logging.html#formatter-objects
    """
    handlers: dict[str, dict[str, Any]] = field(default_factory=_get_default_handlers)
    """A dict in which each key is a handler id and each value is a dict describing how to configure the
    corresponding Handler_ instance. Two handlers are provided, ``console`` and ``queue_listener``.

    .. _Handler: https://docs.python.org/3/library/logging.html#handler-objects
    """
    loggers: dict[str, dict[str, Any]] = field(default_factory=_get_default_loggers)
    """A dict in which each key is a logger name and each value is a dict describing how to configure the
    corresponding Logger_ instance. A ``litestar`` logger is mandatory and will be configured as required.

    .. _Logger: https://docs.python.org/3/library/logging.html#logger-objects
    """
    root: dict[str, dict[str, Any] | list[Any] | str] = field(
        default_factory=lambda: {
            "handlers": ["queue_listener"],
            "level": "INFO",
        }
    )
    """This will be the configuration for the root logger.

    Processing of the configuration will be as for any logger, except that the propagate setting will not be applicable.
    """
    configure_root_logger: bool = field(default=True)
    """Should the root logger be configured, defaults to True for ease of configuration."""
    log_exceptions: Literal["always", "debug", "never"] = field(default="debug")
    """Should exceptions be logged, defaults to log exceptions when 'app.debug == True'"""
    traceback_line_limit: int = field(default=-1)
    """Max number of lines to print for exception traceback.

    .. deprecated:: 2.9.0
        This parameter is deprecated and ignored. It will be removed in a future release.
    """
    exception_logging_handler: ExceptionLoggingHandler | None = field(default=None)
    """Handler function for logging exceptions."""

    def __post_init__(self) -> None:
        if "standard" not in self.formatters:
            self.formatters["standard"] = _get_default_formatters()["standard"]

        if "console" not in self.handlers:
            self.handlers["console"] = _get_default_handlers()["console"]

        if "queue_listener" not in self.handlers:
            self.handlers["queue_listener"] = _get_default_handlers()["queue_listener"]

        if "litestar" not in self.loggers:
            self.loggers["litestar"] = _get_default_loggers()["litestar"]

        if self.log_exceptions != "never" and self.exception_logging_handler is None:
            self.exception_logging_handler = _default_exception_logging_handler_factory(
                is_struct_logger=False, traceback_line_limit=self.traceback_line_limit
            )

    def configure(self) -> GetLogger:
        """Return logger with the given configuration.

        Returns:
            A 'logging.getLogger' like function.
        """

        excluded_fields: set[str] = {
            "configure_root_logger",
            "exception_logging_handler",
            "log_exceptions",
            "propagate",
            "traceback_line_limit",
        }

        if not self.configure_root_logger:
            excluded_fields.add("root")

        if "picologging" in " ".join([handler["class"] for handler in self.handlers.values()]):
            try:
                from picologging import config, getLogger
            except ImportError as e:
                raise MissingDependencyException("picologging") from e

            excluded_fields.add("incremental")
        else:
            from logging import config, getLogger  # type: ignore[no-redef, assignment]

        values = {
            _field.name: getattr(self, _field.name)
            for _field in fields(self)
            if getattr(self, _field.name) is not None and _field.name not in excluded_fields
        }

        config.dictConfig(values)
        return cast("Callable[[str], Logger]", getLogger)

    @staticmethod
    def set_level(logger: Logger, level: int) -> None:
        """Provides a consistent interface to call `setLevel` for all loggers."""
        logger.setLevel(level)


class StructlogEventFilter:
    """Remove keys from the log event.

    Add an instance to the processor chain.

    .. code-block:: python
        :caption: Examples

        structlog.configure(
            ...,
            processors=[
                ...,
                EventFilter(["color_message"]),
                ...,
            ],
        )

    """

    def __init__(self, filter_keys: Iterable[str]) -> None:
        """Initialize the EventFilter.

        Args:
            filter_keys: Iterable of string keys to be excluded from the log event.
        """
        self.filter_keys = filter_keys

    def __call__(self, _: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
        """Receive the log event, and filter keys.

        Args:
            _ ():
            __ ():
            event_dict (): The data to be logged.

        Returns:
            The log event with any key in `self.filter_keys` removed.
        """
        for key in self.filter_keys:
            event_dict.pop(key, None)
        return event_dict


def default_json_serializer(value: EventDict, **_: Any) -> bytes:
    return _msgspec_json_encoder.encode(value)


def stdlib_json_serializer(value: EventDict, **_: Any) -> str:  # pragma: no cover
    return _msgspec_json_encoder.encode(value).decode("utf-8")


def default_structlog_processors(
    as_json: bool = True, json_serializer: Callable[[Any], Any] = default_json_serializer
) -> list[Processor]:  # pyright: ignore
    """Set the default processors for structlog.

    Returns:
        An optional list of processors.
    """
    try:
        import structlog
        from structlog.dev import RichTracebackFormatter

        if as_json:
            return [
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.format_exc_info,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(serializer=json_serializer),
            ]
        return [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(
                colors=True, exception_formatter=RichTracebackFormatter(max_frames=1, show_locals=False, width=80)
            ),
        ]

    except ImportError:
        return []


def default_structlog_standard_lib_processors(as_json: bool = True) -> list[Processor]:  # pyright: ignore
    """Set the default processors for structlog stdlib.

    Returns:
        An optional list of processors.
    """
    try:
        import structlog
        from structlog.dev import RichTracebackFormatter

        if as_json:
            return [
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_log_level,
                structlog.stdlib.ExtraAdder(),
                StructlogEventFilter(["color_message"]),
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(serializer=stdlib_json_serializer),
            ]
        return [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.ExtraAdder(),
            StructlogEventFilter(["color_message"]),
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(
                colors=True, exception_formatter=RichTracebackFormatter(max_frames=1, show_locals=False, width=80)
            ),
        ]
    except ImportError:
        return []


def default_logger_factory(as_json: bool = True) -> Callable[..., WrappedLogger] | None:
    """Set the default logger factory for structlog.

    Returns:
        An optional logger factory.
    """
    try:
        import structlog

        if as_json:
            return structlog.BytesLoggerFactory()
        return structlog.WriteLoggerFactory()
    except ImportError:
        return None


@dataclass
class StructLoggingConfig(BaseLoggingConfig):
    """Configuration class for structlog.

    Notes:
        - requires ``structlog`` to be installed.
    """

    processors: list[Processor] | None = field(default=None)  # pyright: ignore
    """Iterable of structlog logging processors."""
    standard_lib_logging_config: LoggingConfig | None = field(default=None)  # pyright: ignore
    """Optional customized standard logging configuration.

    Use this when you need to modify the standard library outside of the Structlog pre-configured implementation.
    """
    wrapper_class: type[BindableLogger] | None = field(default=None)  # pyright: ignore
    """Structlog bindable logger."""
    context_class: dict[str, Any] | None = None
    """Context class (a 'contextvar' context) for the logger."""
    logger_factory: Callable[..., WrappedLogger] | None = field(default=None)  # pyright: ignore
    """Logger factory to use."""
    cache_logger_on_first_use: bool = field(default=True)
    """Whether to cache the logger configuration and reuse."""
    log_exceptions: Literal["always", "debug", "never"] = field(default="debug")
    """Should exceptions be logged, defaults to log exceptions when 'app.debug == True'"""
    traceback_line_limit: int = field(default=-1)
    """Max number of lines to print for exception traceback.

    .. deprecated:: 2.9.0
        This parameter is deprecated and ignored. It will be removed in a future release.
    """
    exception_logging_handler: ExceptionLoggingHandler | None = field(default=None)
    """Handler function for logging exceptions."""
    pretty_print_tty: bool = field(default=True)
    """Pretty print log output when run from an interactive terminal."""

    def __post_init__(self) -> None:
        if self.processors is None:
            self.processors = default_structlog_processors(as_json=self.as_json())
        if self.logger_factory is None:
            self.logger_factory = default_logger_factory(as_json=self.as_json())
        if self.log_exceptions != "never" and self.exception_logging_handler is None:
            self.exception_logging_handler = _default_exception_logging_handler_factory(
                is_struct_logger=True, traceback_line_limit=self.traceback_line_limit
            )
        try:
            import structlog

            if self.standard_lib_logging_config is None:
                self.standard_lib_logging_config = LoggingConfig(
                    formatters={
                        "standard": {
                            "()": structlog.stdlib.ProcessorFormatter,
                            "processors": default_structlog_standard_lib_processors(as_json=self.as_json()),
                        }
                    }
                )
        except ImportError:
            self.standard_lib_logging_config = LoggingConfig()

    def as_json(self) -> bool:
        return not (sys.stderr.isatty() and self.pretty_print_tty)

    def configure(self) -> GetLogger:
        """Return logger with the given configuration.

        Returns:
            A 'logging.getLogger' like function.
        """
        try:
            import structlog
        except ImportError as e:
            raise MissingDependencyException("structlog") from e

        structlog.configure(
            **{
                k: v
                for k, v in simple_asdict(self).items()
                if k
                not in (
                    "standard_lib_logging_config",
                    "log_exceptions",
                    "traceback_line_limit",
                    "exception_logging_handler",
                    "pretty_print_tty",
                )
            }
        )
        return structlog.get_logger

    @staticmethod
    def set_level(logger: Logger, level: int) -> None:
        """Provides a consistent interface to call `setLevel` for all loggers."""

        try:
            import structlog

            structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(level))
        except ImportError:
            """"""
            return


@deprecated(version="2.6.0", removal_in="3.0.0", alternative="`StructLoggingConfig.set_level`")
def default_wrapper_class(log_level: int = INFO) -> type[BindableLogger] | None:  # pragma: no cover  # pyright: ignore
    try:  # pragma: no cover
        import structlog

        return structlog.make_filtering_bound_logger(log_level)
    except ImportError:
        return None

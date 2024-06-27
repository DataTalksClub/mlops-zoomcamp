import re
from abc import ABC, abstractmethod
from contextlib import suppress
from copy import copy
from dataclasses import dataclass, fields
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Pattern,
    Tuple,
    Union,
    cast,
)

import msgspec
from multidict import CIMultiDict, CIMultiDictProxy, MultiMapping

from litestar._multipart import parse_content_header
from litestar.datastructures.multi_dicts import MultiMixin
from litestar.exceptions import ImproperlyConfiguredException, ValidationException
from litestar.types.empty import Empty
from litestar.utils.dataclass import simple_asdict
from litestar.utils.scope.state import ScopeState

if TYPE_CHECKING:
    from litestar.types.asgi_types import (
        HeaderScope,
        Message,
        RawHeaders,
        RawHeadersList,
        Scope,
    )

__all__ = ("Accept", "CacheControlHeader", "ETag", "Header", "Headers", "MutableScopeHeaders")

ETAG_RE = re.compile(r'([Ww]/)?"(.+)"')
PRINTABLE_ASCII_RE: Pattern[str] = re.compile(r"^[ -~]+$")


def _encode_headers(headers: Iterable[Tuple[str, str]]) -> "RawHeadersList":
    return [(key.lower().encode("latin-1"), value.encode("latin-1")) for key, value in headers]


class Headers(CIMultiDictProxy[str], MultiMixin[str]):
    """An immutable, case-insensitive multi dict for HTTP headers."""

    def __init__(self, headers: Optional[Union[Mapping[str, str], "RawHeaders", MultiMapping]] = None) -> None:
        """Initialize ``Headers``.

        Args:
            headers: Initial value.
        """
        if not isinstance(headers, MultiMapping):
            headers_: Union[Mapping[str, str], List[Tuple[str, str]]] = {}
            if headers:
                if isinstance(headers, Mapping):
                    headers_ = headers  # pyright: ignore
                else:
                    headers_ = [(key.decode("latin-1"), value.decode("latin-1")) for key, value in headers]

            super().__init__(CIMultiDict(headers_))
        else:
            super().__init__(headers)
        self._header_list: Optional[RawHeadersList] = None

    @classmethod
    def from_scope(cls, scope: "Scope") -> "Headers":
        """Create headers from a send-message.

        Args:
            scope: The ASGI connection scope.

        Returns:
            Headers

        Raises:
            ValueError: If the message does not have a ``headers`` key
        """
        connection_state = ScopeState.from_scope(scope)
        if (headers := connection_state.headers) is Empty:
            headers = connection_state.headers = cls(scope["headers"])
        return headers

    def to_header_list(self) -> "RawHeadersList":
        """Raw header value.

        Returns:
            A list of tuples contain the header and header-value as bytes
        """
        # Since ``Headers`` are immutable, this can be cached
        if not self._header_list:
            self._header_list = _encode_headers((key, value) for key in set(self) for value in self.getall(key))
        return self._header_list


class MutableScopeHeaders(MutableMapping):
    """A case-insensitive, multidict-like structure that can be used to mutate headers within a
    :class:`Scope <.types.Scope>`
    """

    def __init__(self, scope: Optional["HeaderScope"] = None) -> None:
        """Initialize ``MutableScopeHeaders`` from a ``HeaderScope``.

        Args:
            scope: The ASGI connection scope.
        """
        self.headers: RawHeadersList
        if scope is not None:
            if not isinstance(scope["headers"], list):
                scope["headers"] = list(scope["headers"])

            self.headers = cast("RawHeadersList", scope["headers"])
        else:
            self.headers = []

    @classmethod
    def from_message(cls, message: "Message") -> "MutableScopeHeaders":
        """Construct a header from a message object.

        Args:
            message: :class:`Message <.types.Message>`.

        Returns:
            MutableScopeHeaders.

        Raises:
            ValueError: If the message does not have a ``headers`` key.
        """
        if "headers" not in message:
            raise ValueError(f"Invalid message type: {message['type']!r}")

        return cls(cast("HeaderScope", message))

    def add(self, key: str, value: str) -> None:
        """Add a header to the scope.

        Notes:
             - This method keeps duplicates.

        Args:
            key: Header key.
            value: Header value.

        Returns:
            None.
        """
        self.headers.append((key.lower().encode("latin-1"), value.encode("latin-1")))

    def getall(self, key: str, default: Optional[List[str]] = None) -> List[str]:
        """Get all values of a header.

        Args:
            key: Header key.
            default: Default value to return if ``name`` is not found.

        Returns:
            A list of strings.

        Raises:
            KeyError: if no header for ``name`` was found and ``default`` is not given.
        """
        name = key.lower()
        values = [
            header_value.decode("latin-1")
            for header_name, header_value in self.headers
            if header_name.decode("latin-1").lower() == name
        ]
        if not values:
            if default:
                return default
            raise KeyError
        return values

    def extend_header_value(self, key: str, value: str) -> None:
        """Extend a multivalued header.

        Notes:
            - A multivalues header is a header that can take a comma separated list.
            - If the header previously did not exist, it will be added.

        Args:
            key: Header key.
            value: Header value to add,

        Returns:
            None
        """
        existing = self.get(key)
        if existing is not None:
            value = ",".join([*existing.split(","), value])
        self[key] = value

    def __getitem__(self, key: str) -> str:
        """Get the first header matching ``name``"""
        name = key.lower()
        for header in self.headers:
            if header[0].decode("latin-1").lower() == name:
                return header[1].decode("latin-1")
        raise KeyError

    def _find_indices(self, key: str) -> List[int]:
        name = key.lower()
        return [i for i, (name_, _) in enumerate(self.headers) if name_.decode("latin-1").lower() == name]

    def __setitem__(self, key: str, value: str) -> None:
        """Set a header in the scope, overwriting duplicates."""
        name_encoded = key.lower().encode("latin-1")
        value_encoded = value.encode("latin-1")
        if indices := self._find_indices(key):
            for i in indices[1:]:
                del self.headers[i]
            self.headers[indices[0]] = (name_encoded, value_encoded)
        else:
            self.headers.append((name_encoded, value_encoded))

    def __delitem__(self, key: str) -> None:
        """Delete all headers matching ``name``"""
        indices = self._find_indices(key)
        for i in indices[::-1]:
            del self.headers[i]

    def __len__(self) -> int:
        """Return the length of the internally stored headers, including duplicates."""
        return len(self.headers)

    def __iter__(self) -> Iterator[str]:
        """Create an iterator of header names including duplicates."""
        return iter(h[0].decode("latin-1") for h in self.headers)


@dataclass
class Header(ABC):
    """An abstract type for HTTP headers."""

    HEADER_NAME: ClassVar[str] = ""

    documentation_only: bool = False
    """Defines the header instance as for OpenAPI documentation purpose only."""

    @abstractmethod
    def _get_header_value(self) -> str:
        """Get the header value as string."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_header(cls, header_value: str) -> "Header":
        """Construct a header from its string representation."""

    def to_header(self, include_header_name: bool = False) -> str:
        """Get the header as string.

        Args:
            include_header_name: should include the header name in the return value. If set to false
                the return value will only include the header value. if set to true the return value
                will be: ``<header name>: <header value>``. Defaults to false.
        """

        if not self.HEADER_NAME:
            raise ImproperlyConfiguredException("Missing header name")

        return (f"{self.HEADER_NAME}: " if include_header_name else "") + self._get_header_value()


@dataclass
class CacheControlHeader(Header):
    """A ``cache-control`` header."""

    HEADER_NAME: ClassVar[str] = "cache-control"

    max_age: Optional[int] = None
    """Accessor for the ``max-age`` directive."""
    s_maxage: Optional[int] = None
    """Accessor for the ``s-maxage`` directive."""
    no_cache: Optional[bool] = None
    """Accessor for the ``no-cache`` directive."""
    no_store: Optional[bool] = None
    """Accessor for the ``no-store`` directive."""
    private: Optional[bool] = None
    """Accessor for the ``private`` directive."""
    public: Optional[bool] = None
    """Accessor for the ``public`` directive."""
    no_transform: Optional[bool] = None
    """Accessor for the ``no-transform`` directive."""
    must_revalidate: Optional[bool] = None
    """Accessor for the ``must-revalidate`` directive."""
    proxy_revalidate: Optional[bool] = None
    """Accessor for the ``proxy-revalidate`` directive."""
    must_understand: Optional[bool] = None
    """Accessor for the ``must-understand`` directive."""
    immutable: Optional[bool] = None
    """Accessor for the ``immutable`` directive."""
    stale_while_revalidate: Optional[int] = None
    """Accessor for the ``stale-while-revalidate`` directive."""

    def _get_header_value(self) -> str:
        """Get the header value as string."""

        cc_items = [
            key.replace("_", "-") if isinstance(value, bool) else f"{key.replace('_', '-')}={value}"
            for key, value in simple_asdict(self, exclude_none=True, exclude={"documentation_only"}).items()
        ]
        return ", ".join(cc_items)

    @classmethod
    def from_header(cls, header_value: str) -> "CacheControlHeader":
        """Create a ``CacheControlHeader`` instance from the header value.

        Args:
            header_value: the header value as string

        Returns:
            An instance of ``CacheControlHeader``
        """

        kwargs: Dict[str, Any] = {}
        field_names = {f.name for f in fields(cls)}
        for cc_item in (stripped for v in header_value.split(",") if (stripped := v.strip())):
            key, *value = cc_item.split("=", maxsplit=1)
            key = key.replace("-", "_")
            if key not in field_names:
                raise ImproperlyConfiguredException("Invalid cache-control header")
            if not value:
                kwargs[key] = True
            else:
                (kwargs[key],) = value

        try:
            return msgspec.convert(kwargs, CacheControlHeader, strict=False)
        except msgspec.ValidationError as exc:
            raise ImproperlyConfiguredException from exc

    @classmethod
    def prevent_storing(cls) -> "CacheControlHeader":
        """Create a ``cache-control`` header with the ``no-store`` directive which indicates that any caches of any kind
        (private or shared) should not store this response.
        """

        return cls(no_store=True)


@dataclass
class ETag(Header):
    """An ``etag`` header."""

    HEADER_NAME: ClassVar[str] = "etag"

    weak: bool = False
    value: Optional[str] = None  # only ASCII characters

    def _get_header_value(self) -> str:
        value = f'"{self.value}"'
        return f"W/{value}" if self.weak else value

    @classmethod
    def from_header(cls, header_value: str) -> "ETag":
        """Construct an ``etag`` header from its string representation.

        Note that this will unquote etag-values
        """
        match = ETAG_RE.match(header_value)
        if not match:
            raise ImproperlyConfiguredException
        weak, value = match.group(1, 2)
        try:
            return cls(weak=bool(weak), value=value)
        except ValueError as exc:
            raise ImproperlyConfiguredException from exc

    def __post_init__(self) -> None:
        if self.documentation_only is False and self.value is None:
            raise ValidationException("value must be set if documentation_only is false")
        if self.value and not PRINTABLE_ASCII_RE.fullmatch(self.value):
            raise ValidationException("value must only contain ASCII printable characters")


class MediaTypeHeader:
    """A helper class for ``Accept`` header parsing."""

    __slots__ = ("maintype", "subtype", "params", "_params_str")

    def __init__(self, type_str: str) -> None:
        # preserve the original parameters, because the order might be
        # changed in the dict
        self._params_str = "".join(type_str.partition(";")[1:])

        full_type, self.params = parse_content_header(type_str)
        self.maintype, _, self.subtype = full_type.partition("/")

    def __str__(self) -> str:
        return f"{self.maintype}/{self.subtype}{self._params_str}"

    @property
    def priority(self) -> Tuple[int, int]:
        # Use fixed point values with two decimals to avoid problems
        # when comparing float values
        quality = 100
        if "q" in self.params:
            with suppress(ValueError):
                quality = int(100 * float(self.params["q"]))

        if self.maintype == "*":
            specificity = 0
        elif self.subtype == "*":
            specificity = 1
        elif not self.params or ("q" in self.params and len(self.params) == 1):
            # no params or 'q' is the only one which we ignore
            specificity = 2
        else:
            specificity = 3

        return quality, specificity

    def match(self, other: "MediaTypeHeader") -> bool:
        return next(
            (False for key, value in self.params.items() if key != "q" and value != other.params.get(key)),
            False
            if self.subtype != "*" and other.subtype != "*" and self.subtype != other.subtype
            else self.maintype == "*" or other.maintype == "*" or self.maintype == other.maintype,
        )


class Accept:
    """An ``Accept`` header."""

    __slots__ = ("_accepted_types",)

    def __init__(self, accept_value: str) -> None:
        self._accepted_types = [MediaTypeHeader(t) for t in accept_value.split(",")]
        self._accepted_types.sort(key=lambda t: t.priority, reverse=True)

    def __len__(self) -> int:
        return len(self._accepted_types)

    def __getitem__(self, key: int) -> str:
        return str(self._accepted_types[key])

    def __iter__(self) -> Iterator[str]:
        return map(str, self._accepted_types)

    def best_match(self, provided_types: List[str], default: Optional[str] = None) -> Optional[str]:
        """Find the best matching media type for the request.

        Args:
            provided_types: A list of media types that can be provided as a response. These types
                            can contain a wildcard ``*`` character in the main- or subtype part.
            default: The media type that is returned if none of the provided types match.

        Returns:
            The best matching media type. If the matching provided type contains wildcard characters,
            they are replaced with the corresponding part of the accepted type. Otherwise the
            provided type is returned as-is.
        """
        types = [MediaTypeHeader(t) for t in provided_types]

        for accepted in self._accepted_types:
            for provided in types:
                if provided.match(accepted):
                    # Return the accepted type with wildcards replaced
                    # by concrete parts from the provided type
                    result = copy(provided)
                    if result.subtype == "*":
                        result.subtype = accepted.subtype
                    if result.maintype == "*":
                        result.maintype = accepted.maintype
                    return str(result)
        return default

    def accepts(self, media_type: str) -> bool:
        """Check if the request accepts the specified media type.

        If multiple media types can be provided, it is better to use :func:`best_match`.

        Args:
            media_type: The media type to check for.

        Returns:
            True if the request accepts ``media_type``.
        """
        return self.best_match([media_type]) == media_type

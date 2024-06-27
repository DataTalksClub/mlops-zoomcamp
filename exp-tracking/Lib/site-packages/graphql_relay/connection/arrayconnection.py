import warnings

# noinspection PyDeprecation
from .array_connection import (
    connection_from_array,
    connection_from_array_slice,
    cursor_for_object_in_connection,
    cursor_to_offset,
    get_offset_with_default,
    offset_to_cursor,
    SizedSliceable,
)

warnings.warn(
    "The 'arrayconnection' module is deprecated. "
    "Functions should be imported from the top-level package instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "connection_from_array",
    "connection_from_array_slice",
    "cursor_for_object_in_connection",
    "cursor_to_offset",
    "get_offset_with_default",
    "offset_to_cursor",
    "SizedSliceable",
]

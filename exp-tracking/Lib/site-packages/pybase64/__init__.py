from typing import Any

from ._license import _license
from ._version import __version__

try:
    from ._pybase64 import (  # noqa: F401
        _get_simd_name,
        _get_simd_path,
        b64decode,
        b64decode_as_bytearray,
        b64encode,
        b64encode_as_string,
        encodebytes,
    )
except ImportError:
    from ._fallback import (  # noqa: F401
        _get_simd_name,
        _get_simd_path,
        b64decode,
        b64decode_as_bytearray,
        b64encode,
        b64encode_as_string,
        encodebytes,
    )


def get_license_text() -> str:
    """Returns pybase64 license information as a :class:`str` object.

    The result includes libbase64 license information as well.
    """
    return _license


def get_version() -> str:
    """Returns pybase64 version as a :class:`str` object.

    The result reports if the C extension is used or not.
    e.g. `1.0.0 (C extension active - AVX2)`
    """
    simd_name = _get_simd_name(_get_simd_path())
    if simd_name != "fallback":
        return f"{__version__} (C extension active - {simd_name})"
    return f"{__version__} (C extension inactive)"


def standard_b64encode(s: Any) -> bytes:
    """Encode bytes using the standard Base64 alphabet.

    Argument ``s`` is a :term:`bytes-like object` to encode.

    The result is returned as a :class:`bytes` object.
    """
    return b64encode(s)


def standard_b64decode(s: Any) -> bytes:
    """Decode bytes encoded with the standard Base64 alphabet.

    Argument ``s`` is a :term:`bytes-like object` or ASCII string to
    decode.

    The result is returned as a :class:`bytes` object.

    A :exc:`binascii.Error` is raised if the input is incorrectly padded.

    Characters that are not in the standard alphabet are discarded prior
    to the padding check.
    """
    return b64decode(s)


def urlsafe_b64encode(s: Any) -> bytes:
    """Encode bytes using the URL- and filesystem-safe Base64 alphabet.

    Argument ``s`` is a :term:`bytes-like object` to encode.

    The result is returned as a :class:`bytes` object.

    The alphabet uses '-' instead of '+' and '_' instead of '/'.
    """
    return b64encode(s, b"-_")


def urlsafe_b64decode(s: Any) -> bytes:
    """Decode bytes using the URL- and filesystem-safe Base64 alphabet.

    Argument ``s`` is a :term:`bytes-like object` or ASCII string to
    decode.

    The result is returned as a :class:`bytes` object.

    A :exc:`binascii.Error` is raised if the input is incorrectly padded.

    Characters that are not in the URL-safe base-64 alphabet, and are not
    a plus '+' or slash '/', are discarded prior to the padding check.

    The alphabet uses '-' instead of '+' and '_' instead of '/'.
    """
    return b64decode(s, b"-_")

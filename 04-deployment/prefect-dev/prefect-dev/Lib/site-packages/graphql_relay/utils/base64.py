from base64 import b64encode, b64decode
import binascii

__all__ = ["base64", "unbase64"]

Base64String = str


def base64(s: str) -> Base64String:
    """Encode the string s using Base64."""
    b: bytes = s.encode("utf-8") if isinstance(s, str) else s
    return b64encode(b).decode("ascii")


def unbase64(s: Base64String) -> str:
    """Decode the string s using Base64."""
    try:
        b: bytes = s.encode("ascii") if isinstance(s, str) else s
    except UnicodeEncodeError:
        return ""
    try:
        return b64decode(b).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return ""

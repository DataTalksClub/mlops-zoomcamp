from typing import Any

from litestar.exceptions.base_exceptions import LitestarException
from litestar.status_codes import WS_1000_NORMAL_CLOSURE

__all__ = ("WebSocketDisconnect", "WebSocketException")


class WebSocketException(LitestarException):
    """Exception class for websocket related events."""

    code: int
    """Exception code. For custom exceptions, this should be a number in the 4000+ range. Other codes can be found in
    ``litestar.status_code`` with the ``WS_`` prefix.
    """

    def __init__(self, *args: Any, detail: str, code: int = 4500) -> None:
        """Initialize ``WebSocketException``.

        Args:
            *args: Any exception args.
            detail: Exception details.
            code: Exception code. Should be a number in the >= 1000.
        """
        super().__init__(*args, detail=detail)
        self.code = code


class WebSocketDisconnect(WebSocketException):
    """Exception class for websocket disconnect events."""

    def __init__(self, *args: Any, detail: str, code: int = WS_1000_NORMAL_CLOSURE) -> None:
        """Initialize ``WebSocketDisconnect``.

        Args:
            *args: Any exception args.
            detail: Exception details.
            code: Exception code. Should be a number in the >= 1000.
        """
        super().__init__(*args, detail=detail, code=code)

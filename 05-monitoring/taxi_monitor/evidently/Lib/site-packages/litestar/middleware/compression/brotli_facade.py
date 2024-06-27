from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from litestar.enums import CompressionEncoding
from litestar.exceptions import MissingDependencyException
from litestar.middleware.compression.facade import CompressionFacade

try:
    from brotli import MODE_FONT, MODE_GENERIC, MODE_TEXT, Compressor
except ImportError as e:
    raise MissingDependencyException("brotli") from e


if TYPE_CHECKING:
    from io import BytesIO

    from litestar.config.compression import CompressionConfig


class BrotliCompression(CompressionFacade):
    __slots__ = ("compressor", "buffer", "compression_encoding")

    encoding = CompressionEncoding.BROTLI

    def __init__(
        self,
        buffer: BytesIO,
        compression_encoding: Literal[CompressionEncoding.BROTLI] | str,
        config: CompressionConfig,
    ) -> None:
        self.buffer = buffer
        self.compression_encoding = compression_encoding
        modes: dict[Literal["generic", "text", "font"], int] = {
            "text": int(MODE_TEXT),
            "font": int(MODE_FONT),
            "generic": int(MODE_GENERIC),
        }
        self.compressor = Compressor(
            quality=config.brotli_quality,
            mode=modes[config.brotli_mode],
            lgwin=config.brotli_lgwin,
            lgblock=config.brotli_lgblock,
        )

    def write(self, body: bytes) -> None:
        self.buffer.write(self.compressor.process(body))
        self.buffer.write(self.compressor.flush())

    def close(self) -> None:
        self.buffer.write(self.compressor.finish())

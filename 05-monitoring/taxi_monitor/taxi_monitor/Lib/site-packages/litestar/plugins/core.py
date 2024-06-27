from __future__ import annotations

import inspect
from inspect import Signature
from typing import Any

import msgspec

from litestar.plugins import DIPlugin

__all__ = ("MsgspecDIPlugin",)


class MsgspecDIPlugin(DIPlugin):
    def has_typed_init(self, type_: Any) -> bool:
        return type(type_) is type(msgspec.Struct)  # noqa: E721

    def get_typed_init(self, type_: Any) -> tuple[Signature, dict[str, Any]]:
        parameters = []
        type_hints = {}
        for field_info in msgspec.structs.fields(type_):
            type_hints[field_info.name] = field_info.type
            parameters.append(
                inspect.Parameter(
                    name=field_info.name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation=field_info.type,
                    default=field_info.default,
                )
            )
        return inspect.Signature(parameters), type_hints

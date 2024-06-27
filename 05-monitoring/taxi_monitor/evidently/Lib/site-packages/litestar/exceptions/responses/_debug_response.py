from __future__ import annotations

from html import escape
from inspect import getinnerframes
from pathlib import Path
from traceback import format_exception
from typing import TYPE_CHECKING, Any

from litestar.enums import MediaType
from litestar.response import Response
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from litestar.utils import get_name

__all__ = (
    "create_debug_response",
    "create_exception_html",
    "create_frame_html",
    "create_html_response_content",
    "create_line_html",
    "create_plain_text_response_content",
    "get_symbol_name",
)


if TYPE_CHECKING:
    from inspect import FrameInfo

    from litestar.connection import Request
    from litestar.types import TypeEncodersMap

tpl_dir = Path(__file__).parent / "templates"


def get_symbol_name(frame: FrameInfo) -> str:
    """Return full name of the function that is being executed by the given frame.

    Args:
        frame: An instance of [FrameInfo](https://docs.python.org/3/library/inspect.html#inspect.FrameInfo).

    Notes:
        - class detection assumes standard names (self and cls) of params.
        - if current class name can not be determined only function (method) name will be returned.
        - we can not distinguish static methods from ordinary functions at the moment.

    Returns:
        A string containing full function name.
    """

    locals_dict = frame.frame.f_locals
    # this piece assumes that the code uses standard names "self" and "cls"
    # in instance and class methods
    instance_or_cls = inst if (inst := locals_dict.get("self")) is not None else locals_dict.get("cls")

    classname = f"{get_name(instance_or_cls)}." if instance_or_cls is not None else ""

    return f"{classname}{frame.function}"


def create_line_html(
    line: str,
    line_no: int,
    frame_index: int,
    idx: int,
) -> str:
    """Produce HTML representation of a line including real line number in the source code.

    Args:
        line: A string representing the current line.
        line_no: The line number associated with the executed line.
        frame_index: Index of the executed line in the code context.
        idx: Index of the current line in the code context.

    Returns:
        A string containing HTML representation of the given line.
    """
    template = '<tr class="{line_class}"><td class="line_no">{line_no}</td><td class="code_line">{line}</td></tr>'
    data = {
        # line_no - frame_index produces actual line number of the very first line in the frame code context.
        # so adding index (aka relative number) of a line in the code context we can calculate its actual number in the source file,
        "line_no": line_no - frame_index + idx,
        "line": escape(line).replace(" ", "&nbsp"),
        "line_class": "executed-line" if idx == frame_index else "",
    }
    return template.format(**data)


def create_frame_html(frame: FrameInfo, collapsed: bool) -> str:
    """Produce HTML representation of the given frame object including filename containing source code and name of the
    function being executed.

    Args:
        frame: An instance of [FrameInfo](https://docs.python.org/3/library/inspect.html#inspect.FrameInfo).
        collapsed: Flag controlling whether frame should be collapsed on the page load.

    Returns:
        A string containing HTML representation of the execution frame.
    """
    frame_tpl = (tpl_dir / "frame.html").read_text()

    code_lines: list[str] = [
        create_line_html(line, frame.lineno, frame.index or 0, idx) for idx, line in enumerate(frame.code_context or [])
    ]
    data = {
        "file": escape(frame.filename),
        "line": frame.lineno,
        "symbol_name": escape(get_symbol_name(frame)),
        "code": "".join(code_lines),
        "frame_class": "collapsed" if collapsed else "",
    }
    return frame_tpl.format(**data)


def create_exception_html(exc: BaseException, line_limit: int) -> str:
    """Produce HTML representation of the exception frames.

    Args:
        exc: An Exception instance to generate.
        line_limit: Number of lines of code context to return, which are centered around the executed line.

    Returns:
        A string containing HTML representation of the execution frames related to the exception.
    """
    frames = getinnerframes(exc.__traceback__, line_limit) if exc.__traceback__ else []
    result = [create_frame_html(frame=frame, collapsed=idx > 0) for idx, frame in enumerate(reversed(frames))]
    return "".join(result)


def create_html_response_content(exc: Exception, request: Request, line_limit: int = 15) -> str:
    """Given an exception, produces its traceback in HTML.

    Args:
        exc: An Exception instance to render debug response from.
        request: A :class:`Request <litestar.connection.Request>` instance.
        line_limit: Number of lines of code context to return, which are centered around the executed line.

    Returns:
        A string containing HTML page with exception traceback.
    """
    exception_data: list[str] = [create_exception_html(exc, line_limit)]
    cause = exc.__cause__
    while cause:
        cause_data = create_exception_html(cause, line_limit)
        cause_header = '<h4 class="cause-header">The above exception was caused by</h4>'
        cause_error_description = f"<h3><span>{escape(str(cause))}</span></h3>"
        cause_error = f"<h4><span>{escape(cause.__class__.__name__)}</span></h4>"
        exception_data.append(
            f'<div class="cause-wrapper">{cause_header}{cause_error}{cause_error_description}{cause_data}</div>'
        )
        cause = cause.__cause__

    scripts = (tpl_dir / "scripts.js").read_text()
    styles = (tpl_dir / "styles.css").read_text()
    body_tpl = (tpl_dir / "body.html").read_text()
    return body_tpl.format(
        scripts=scripts,
        styles=styles,
        error=f"<span>{escape(exc.__class__.__name__)}</span> on {request.method} {escape(request.url.path)}",
        error_description=escape(str(exc)),
        exception_data="".join(exception_data),
    )


def create_plain_text_response_content(exc: Exception) -> str:
    """Given an exception, produces its traceback in plain text.

    Args:
        exc: An Exception instance to render debug response from.

    Returns:
        A string containing exception traceback.
    """
    return "".join(format_exception(type(exc), value=exc, tb=exc.__traceback__))


def create_debug_response(request: Request, exc: Exception) -> Response:
    """Create debug response either in plain text or HTML depending on client capabilities.

    Args:
        request: A :class:`Request <litestar.connection.Request>` instance.
        exc: An Exception instance to render debug response from.

    Returns:
        A response with a rendered exception traceback.
    """
    if MediaType.HTML in request.headers.get("accept", ""):
        content: Any = create_html_response_content(exc=exc, request=request)
        media_type = MediaType.HTML
    elif MediaType.JSON in request.headers.get("accept", ""):
        content = {"details": create_plain_text_response_content(exc), "status_code": HTTP_500_INTERNAL_SERVER_ERROR}
        media_type = MediaType.JSON
    else:
        content = create_plain_text_response_content(exc)
        media_type = MediaType.TEXT

    return Response(
        content=content,
        media_type=media_type,
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        type_encoders=_get_type_encoders_for_request(request),
    )


def _get_type_encoders_for_request(request: Request) -> TypeEncodersMap | None:
    try:
        return request.route_handler.resolve_type_encoders()
    # we might be in a 404, or before we could resolve the handler, so this
    # could potentially error out. In this case we fall back on the application
    # type encoders
    except (KeyError, AttributeError):
        return request.app.type_encoders

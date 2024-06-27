try:
    import rich_click as click
except ImportError:
    import click  # type: ignore[no-redef]
from rich.prompt import Confirm

from litestar import Litestar
from litestar.cli._utils import LitestarCLIException, LitestarGroup, console
from litestar.middleware import DefineMiddleware
from litestar.middleware.session import SessionMiddleware
from litestar.middleware.session.server_side import ServerSideSessionBackend
from litestar.utils import is_class_and_subclass

__all__ = ("clear_sessions_command", "delete_session_command", "get_session_backend", "sessions_group")


def get_session_backend(app: Litestar) -> ServerSideSessionBackend:
    """Get the session backend used by a ``Litestar`` app."""
    for middleware in app.middleware:
        if isinstance(middleware, DefineMiddleware):
            if not is_class_and_subclass(middleware.middleware, SessionMiddleware):
                continue
            backend = middleware.kwargs["backend"]
            if not isinstance(backend, ServerSideSessionBackend):
                raise LitestarCLIException("Only server-side backends are supported")
            return backend
    raise LitestarCLIException("Session middleware not installed")


@click.group(cls=LitestarGroup, name="sessions")
def sessions_group() -> None:
    """Manage server-side sessions."""


@sessions_group.command("delete")  # type: ignore[misc]
@click.argument("session-id")
def delete_session_command(session_id: str, app: Litestar) -> None:
    """Delete a specific session."""
    import anyio

    backend = get_session_backend(app)
    store = backend.config.get_store_from_app(app)

    if Confirm.ask(f"Delete session {session_id!r}?"):
        anyio.run(backend.delete, session_id, store)
        console.print(f"[green]Deleted session {session_id!r}")


@sessions_group.command("clear")  # type: ignore[misc]
def clear_sessions_command(app: Litestar) -> None:
    """Delete all sessions."""
    import anyio

    backend = get_session_backend(app)
    store = backend.config.get_store_from_app(app)
    if not hasattr(store, "delete_all"):
        raise LitestarCLIException(f"{type(store)} does not support clearing all sessions")

    if Confirm.ask("[red]Delete all sessions?"):
        anyio.run(store.delete_all)  # pyright: ignore
        console.print("[green]All active sessions deleted")

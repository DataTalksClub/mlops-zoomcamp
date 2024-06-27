from pathlib import Path

import msgspec
from click import Path as ClickPath

try:
    import rich_click as click
except ImportError:
    import click  # type: ignore[no-redef]

from yaml import dump as dump_yaml

from litestar import Litestar
from litestar._openapi.typescript_converter.converter import (
    convert_openapi_to_typescript,
)
from litestar.cli._utils import JSBEAUTIFIER_INSTALLED, LitestarCLIException, LitestarGroup
from litestar.serialization import encode_json, get_serializer

__all__ = ("generate_openapi_schema", "generate_typescript_specs", "schema_group")


@click.group(cls=LitestarGroup, name="schema")
def schema_group() -> None:
    """Manage server-side OpenAPI schemas."""


def _generate_openapi_schema(app: Litestar, output: Path) -> None:
    """Generate an OpenAPI Schema."""
    serializer = get_serializer(app.type_encoders)
    if output.suffix in (".yml", ".yaml"):
        content = dump_yaml(
            msgspec.to_builtins(app.openapi_schema.to_schema(), enc_hook=serializer),
            default_flow_style=False,
            encoding="utf-8",
        )
    else:
        content = msgspec.json.format(
            encode_json(app.openapi_schema.to_schema(), serializer=serializer),
            indent=4,
        )

    try:
        output.write_bytes(content)
    except OSError as e:  # pragma: no cover
        raise LitestarCLIException(f"failed to write schema to path {output}") from e


@schema_group.command("openapi")  # type: ignore[misc]
@click.option(
    "--output",
    help="output file path",
    type=ClickPath(dir_okay=False, path_type=Path),
    default=Path("openapi_schema.json"),
    show_default=True,
)
def generate_openapi_schema(app: Litestar, output: Path) -> None:
    """Generate an OpenAPI Schema."""
    _generate_openapi_schema(app, output)


@schema_group.command("typescript")  # type: ignore[misc]
@click.option(
    "--output",
    help="output file path",
    type=ClickPath(dir_okay=False, path_type=Path),
    default=Path("api-specs.ts"),
    show_default=True,
)
@click.option("--namespace", help="namespace to use for the typescript specs", type=str, default="API")
def generate_typescript_specs(app: Litestar, output: Path, namespace: str) -> None:
    """Generate TypeScript specs from the OpenAPI schema."""
    if JSBEAUTIFIER_INSTALLED:  # pragma: no cover
        from jsbeautifier import Beautifier

        beautifier = Beautifier()
    else:
        beautifier = None
    try:
        specs = convert_openapi_to_typescript(app.openapi_schema, namespace)
        # beautifier will be defined if JSBEAUTIFIER_INSTALLED is True
        specs_output = (
            beautifier.beautify(specs.write()) if JSBEAUTIFIER_INSTALLED and beautifier else specs.write()  # pyright: ignore
        )
        output.write_text(specs_output)
    except OSError as e:  # pragma: no cover
        raise LitestarCLIException(f"failed to write schema to path {output}") from e

"""Module that contains the command line application."""

# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m griffe` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `griffe.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `griffe.__main__` in `sys.modules`.

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Callable, Sequence

import colorama

from griffe import debug
from griffe.diff import find_breaking_changes
from griffe.encoders import JSONEncoder
from griffe.enumerations import ExplanationStyle, Parser
from griffe.exceptions import ExtensionError, GitError
from griffe.extensions.base import load_extensions
from griffe.git import get_latest_tag, get_repo_root
from griffe.loader import GriffeLoader, load, load_git
from griffe.logger import get_logger

if TYPE_CHECKING:
    from griffe.extensions.base import Extensions, ExtensionType


DEFAULT_LOG_LEVEL = os.getenv("GRIFFE_LOG_LEVEL", "INFO").upper()
logger = get_logger(__name__)


class _DebugInfo(argparse.Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        debug.print_debug_info()
        sys.exit(0)


def _print_data(data: str, output_file: str | IO | None) -> None:
    if isinstance(output_file, str):
        with open(output_file, "w") as fd:
            print(data, file=fd)
    else:
        if output_file is None:
            output_file = sys.stdout
        print(data, file=output_file)


def _load_packages(
    packages: Sequence[str],
    *,
    extensions: Extensions | None = None,
    search_paths: Sequence[str | Path] | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    resolve_aliases: bool = True,
    resolve_implicit: bool = False,
    resolve_external: bool | None = None,
    allow_inspection: bool = True,
    force_inspection: bool = False,
    store_source: bool = True,
    find_stubs_package: bool = False,
) -> GriffeLoader:
    # Create a single loader.
    loader = GriffeLoader(
        extensions=extensions,
        search_paths=search_paths,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        allow_inspection=allow_inspection,
        force_inspection=force_inspection,
        store_source=store_source,
    )

    # Load each package.
    for package in packages:
        if not package:
            logger.debug("Empty package name, continuing")
            continue
        logger.info(f"Loading package {package}")
        try:
            loader.load(package, try_relative_path=True, find_stubs_package=find_stubs_package)
        except ModuleNotFoundError as error:
            logger.error(f"Could not find package {package}: {error}")  # noqa: TRY400
        except ImportError as error:
            logger.exception(f"Tried but could not import package {package}: {error}")  # noqa: TRY401
    logger.info("Finished loading packages")

    # Resolve aliases.
    if resolve_aliases:
        logger.info("Starting alias resolution")
        unresolved, iterations = loader.resolve_aliases(implicit=resolve_implicit, external=resolve_external)
        if unresolved:
            logger.info(f"{len(unresolved)} aliases were still unresolved after {iterations} iterations")
        else:
            logger.info(f"All aliases were resolved after {iterations} iterations")
    return loader


_level_choices = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def _extensions_type(value: str) -> Sequence[str | dict[str, Any]]:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value.split(",")


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    usage = "%(prog)s [GLOBAL_OPTS...] COMMAND [COMMAND_OPTS...]"
    description = "Signatures for entire Python programs. "
    "Extract the structure, the frame, the skeleton of your project, "
    "to generate API documentation or find breaking changes in your API."
    parser = argparse.ArgumentParser(add_help=False, usage=usage, description=description, prog="griffe")

    main_help = "Show this help message and exit. Commands also accept the -h/--help option."
    subcommand_help = "Show this help message and exit."

    global_options = parser.add_argument_group(title="Global options")
    global_options.add_argument("-h", "--help", action="help", help=main_help)
    global_options.add_argument("-V", "--version", action="version", version=f"%(prog)s {debug.get_version()}")
    global_options.add_argument("--debug-info", action=_DebugInfo, help="Print debug information.")

    def add_common_options(subparser: argparse.ArgumentParser) -> None:
        common_options = subparser.add_argument_group(title="Common options")
        common_options.add_argument("-h", "--help", action="help", help=subcommand_help)
        search_options = subparser.add_argument_group(title="Search options")
        search_options.add_argument(
            "-s",
            "--search",
            dest="search_paths",
            action="append",
            type=Path,
            help="Paths to search packages into.",
        )
        search_options.add_argument(
            "-y",
            "--sys-path",
            dest="append_sys_path",
            action="store_true",
            help="Whether to append `sys.path` to search paths specified with `-s`.",
        )
        loading_options = subparser.add_argument_group(title="Loading options")
        loading_options.add_argument(
            "-B",
            "--find-stubs-packages",
            dest="find_stubs_package",
            action="store_true",
            default=False,
            help="Whether to look for stubs-only packages and merge them with concrete ones.",
        )
        loading_options.add_argument(
            "-e",
            "--extensions",
            default={},
            type=_extensions_type,
            help="A list of extensions to use.",
        )
        loading_options.add_argument(
            "-X",
            "--no-inspection",
            dest="allow_inspection",
            action="store_false",
            default=True,
            help="Disallow inspection of builtin/compiled/not found modules.",
        )
        loading_options.add_argument(
            "-x",
            "--force-inspection",
            dest="force_inspection",
            action="store_true",
            default=False,
            help="Force inspection of everything, even when sources are found.",
        )
        debug_options = subparser.add_argument_group(title="Debugging options")
        debug_options.add_argument(
            "-L",
            "--log-level",
            metavar="LEVEL",
            default=DEFAULT_LOG_LEVEL,
            choices=_level_choices,
            type=str.upper,
            help="Set the log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.",
        )

    # ========= SUBPARSERS ========= #
    subparsers = parser.add_subparsers(
        dest="subcommand",
        title="Commands",
        metavar="COMMAND",
        prog="griffe",
        required=True,
    )

    def add_subparser(command: str, text: str, **kwargs: Any) -> argparse.ArgumentParser:
        return subparsers.add_parser(command, add_help=False, help=text, description=text, **kwargs)

    # ========= DUMP PARSER ========= #
    dump_parser = add_subparser("dump", "Load package-signatures and dump them as JSON.")
    dump_options = dump_parser.add_argument_group(title="Dump options")
    dump_options.add_argument("packages", metavar="PACKAGE", nargs="+", help="Packages to find, load and dump.")
    dump_options.add_argument(
        "-f",
        "--full",
        action="store_true",
        default=False,
        help="Whether to dump full data in JSON.",
    )
    dump_options.add_argument(
        "-o",
        "--output",
        default=sys.stdout,
        help="Output file. Supports templating to output each package in its own file, with `{package}`.",
    )
    dump_options.add_argument(
        "-d",
        "--docstyle",
        dest="docstring_parser",
        default=None,
        type=Parser,
        help="The docstring style to parse.",
    )
    dump_options.add_argument(
        "-D",
        "--docopts",
        dest="docstring_options",
        default={},
        type=json.loads,
        help="The options for the docstring parser.",
    )
    dump_options.add_argument(
        "-r",
        "--resolve-aliases",
        action="store_true",
        help="Whether to resolve aliases.",
    )
    dump_options.add_argument(
        "-I",
        "--resolve-implicit",
        action="store_true",
        help="Whether to resolve implicitely exported aliases as well. "
        "Aliases are explicitely exported when defined in `__all__`.",
    )
    dump_options.add_argument(
        "-U",
        "--resolve-external",
        dest="resolve_external",
        action="store_true",
        help="Always resolve aliases pointing to external/unknown modules (not loaded directly)."
        "Default is to resolve only from one module to its private sibling (`ast` -> `_ast`).",
    )
    dump_options.add_argument(
        "--no-resolve-external",
        dest="resolve_external",
        action="store_false",
        help="Never resolve aliases pointing to external/unknown modules (not loaded directly)."
        "Default is to resolve only from one module to its private sibling (`ast` -> `_ast`).",
    )
    dump_options.add_argument(
        "-S",
        "--stats",
        action="store_true",
        help="Show statistics at the end.",
    )
    add_common_options(dump_parser)

    # ========= CHECK PARSER ========= #
    check_parser = add_subparser("check", "Check for API breakages or possible improvements.")
    check_options = check_parser.add_argument_group(title="Check options")
    check_options.add_argument("package", metavar="PACKAGE", help="Package to find, load and check, as path.")
    check_options.add_argument(
        "-a",
        "--against",
        metavar="REF",
        help="Older Git reference (commit, branch, tag) to check against. Default: load latest tag.",
    )
    check_options.add_argument(
        "-b",
        "--base-ref",
        metavar="BASE_REF",
        help="Git reference (commit, branch, tag) to check. Default: load current code.",
    )
    check_options.add_argument(
        "--color",
        dest="color",
        action="store_true",
        default=None,
        help="Force enable colors in the output.",
    )
    check_options.add_argument(
        "--no-color",
        dest="color",
        action="store_false",
        default=None,
        help="Force disable colors in the output.",
    )
    check_options.add_argument("-v", "--verbose", action="store_true", help="Verbose output.")
    formats = ("oneline", "verbose")
    check_options.add_argument("-f", "--format", dest="style", choices=formats, default=None, help="Output format.")
    add_common_options(check_parser)

    return parser


def dump(
    packages: Sequence[str],
    *,
    output: str | IO | None = None,
    full: bool = False,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    extensions: Sequence[str | dict[str, Any] | ExtensionType | type[ExtensionType]] | None = None,
    resolve_aliases: bool = False,
    resolve_implicit: bool = False,
    resolve_external: bool | None = None,
    search_paths: Sequence[str | Path] | None = None,
    find_stubs_package: bool = False,
    append_sys_path: bool = False,
    allow_inspection: bool = True,
    force_inspection: bool = False,
    stats: bool = False,
) -> int:
    """Load packages data and dump it as JSON.

    Parameters:
        packages: The packages to load and dump.
        output: Where to output the JSON-serialized data.
        full: Whether to output full or minimal data.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        resolve_aliases: Whether to resolve aliases (indirect objects references).
        resolve_implicit: Whether to resolve every alias or only the explicitly exported ones.
        resolve_external: Whether to load additional, unspecified modules to resolve aliases.
            Default is to resolve only from one module to its private sibling (`ast` -> `_ast`).
        extensions: The extensions to use.
        search_paths: The paths to search into.
        find_stubs_package: Whether to search for stubs-only packages.
            If both the package and its stubs are found, they'll be merged together.
            If only the stubs are found, they'll be used as the package itself.
        append_sys_path: Whether to append the contents of `sys.path` to the search paths.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.
        force_inspection: Whether to force using dynamic analysis when loading data.
        stats: Whether to compute and log stats about loading.

    Returns:
        `0` for success, `1` for failure.
    """
    # Prepare options.
    per_package_output = False
    if isinstance(output, str) and output.format(package="package") != output:
        per_package_output = True

    search_paths = list(search_paths) if search_paths else []
    if append_sys_path:
        search_paths.extend(sys.path)

    try:
        loaded_extensions = load_extensions(*(extensions or ()))
    except ExtensionError as error:
        logger.exception(str(error))  # noqa: TRY401
        return 1

    # Load packages.
    loader = _load_packages(
        packages,
        extensions=loaded_extensions,
        search_paths=search_paths,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        resolve_aliases=resolve_aliases,
        resolve_implicit=resolve_implicit,
        resolve_external=resolve_external,
        allow_inspection=allow_inspection,
        force_inspection=force_inspection,
        store_source=False,
        find_stubs_package=find_stubs_package,
    )
    data_packages = loader.modules_collection.members

    # Serialize and dump packages.
    started = datetime.now(tz=timezone.utc)
    if per_package_output:
        for package_name, data in data_packages.items():
            serialized = data.as_json(indent=2, full=full)
            _print_data(serialized, output.format(package=package_name))  # type: ignore[union-attr]
    else:
        serialized = json.dumps(data_packages, cls=JSONEncoder, indent=2, full=full)
        _print_data(serialized, output)
    elapsed = datetime.now(tz=timezone.utc) - started

    if stats:
        loader_stats = loader.stats()
        loader_stats.time_spent_serializing = elapsed.microseconds
        logger.info(loader_stats.as_text())

    return 0 if len(data_packages) == len(packages) else 1


def check(
    package: str | Path,
    against: str | None = None,
    against_path: str | Path | None = None,
    *,
    base_ref: str | None = None,
    extensions: Sequence[str | dict[str, Any] | ExtensionType | type[ExtensionType]] | None = None,
    search_paths: Sequence[str | Path] | None = None,
    append_sys_path: bool = False,
    find_stubs_package: bool = False,
    allow_inspection: bool = True,
    force_inspection: bool = False,
    verbose: bool = False,
    color: bool | None = None,
    style: str | ExplanationStyle | None = None,
) -> int:
    """Check for API breaking changes in two versions of the same package.

    Parameters:
        package: The package to load and check.
        against: Older Git reference (commit, branch, tag) to check against.
        against_path: Path when the "against" reference is checked out.
        base_ref: Git reference (commit, branch, tag) to check.
        extensions: The extensions to use.
        search_paths: The paths to search into.
        append_sys_path: Whether to append the contents of `sys.path` to the search paths.
        allow_inspection: Whether to allow inspecting modules when visiting them is not possible.
        force_inspection: Whether to force using dynamic analysis when loading data.
        verbose: Use a verbose output.

    Returns:
        `0` for success, `1` for failure.
    """
    # Prepare options.
    search_paths = list(search_paths) if search_paths else []
    if append_sys_path:
        search_paths.extend(sys.path)

    try:
        against = against or get_latest_tag(package)
    except GitError as error:
        print(f"griffe: error: {error}", file=sys.stderr)
        return 2
    against_path = against_path or package
    repository = get_repo_root(against_path)

    try:
        loaded_extensions = load_extensions(*(extensions or ()))
    except ExtensionError as error:
        logger.exception(str(error))  # noqa: TRY401
        return 1

    # Load old and new version of the package.
    old_package = load_git(
        against_path,
        ref=against,
        repo=repository,
        extensions=loaded_extensions,
        search_paths=search_paths,
        allow_inspection=allow_inspection,
        force_inspection=force_inspection,
    )
    if base_ref:
        new_package = load_git(
            package,
            ref=base_ref,
            repo=repository,
            extensions=loaded_extensions,
            search_paths=search_paths,
            allow_inspection=allow_inspection,
            force_inspection=force_inspection,
            find_stubs_package=find_stubs_package,
        )
    else:
        new_package = load(
            package,
            try_relative_path=True,
            extensions=loaded_extensions,
            search_paths=search_paths,
            allow_inspection=allow_inspection,
            force_inspection=force_inspection,
            find_stubs_package=find_stubs_package,
        )

    # Find and display API breakages.
    breakages = list(find_breaking_changes(old_package, new_package))

    colorama.deinit()
    colorama.init(strip=color if color is None else not color)
    if style is None:
        style = ExplanationStyle.VERBOSE if verbose else ExplanationStyle.ONE_LINE
    else:
        style = ExplanationStyle(style)
    for breakage in breakages:
        print(breakage.explain(style=style), file=sys.stderr)

    if breakages:
        return 1
    return 0


def main(args: list[str] | None = None) -> int:
    """Run the main program.

    This function is executed when you type `griffe` or `python -m griffe`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    # Parse arguments.
    parser = get_parser()
    opts: argparse.Namespace = parser.parse_args(args)
    opts_dict = opts.__dict__
    opts_dict.pop("debug_info")
    subcommand = opts_dict.pop("subcommand")

    # Initialize logging.
    log_level = opts_dict.pop("log_level", DEFAULT_LOG_LEVEL)
    try:
        level = getattr(logging, log_level)
    except AttributeError:
        choices = "', '".join(_level_choices)
        print(
            f"griffe: error: invalid log level '{log_level}' (choose from '{choices}')",
            file=sys.stderr,
        )
        return 1
    else:
        logging.basicConfig(format="%(levelname)-10s %(message)s", level=level)

    # Run subcommand.
    commands: dict[str, Callable[..., int]] = {"check": check, "dump": dump}
    return commands[subcommand](**opts_dict)


__all__ = ["check", "dump", "get_parser", "main"]

# -----------------------------------------------------------------------------
# Copyright © 2009- The QtPy Contributors
#
# Released under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provide a CLI to allow configuring developer settings, including mypy."""

# Standard library imports
import argparse
import json
import textwrap


def print_version():
    """Print the current version of the package."""
    import qtpy

    print("QtPy version", qtpy.__version__)


def get_api_status():
    """Get the status of each Qt API usage."""
    import qtpy

    return {name: name == qtpy.API for name in qtpy.API_NAMES}


def generate_mypy_args():
    """Generate a string with always-true/false args to pass to mypy."""
    options = {False: "--always-false", True: "--always-true"}

    apis_active = get_api_status()
    return " ".join(
        f"{options[is_active]}={name.upper()}"
        for name, is_active in apis_active.items()
    )


def generate_pyright_config_json():
    """Generate Pyright config to be used in `pyrightconfig.json`."""
    apis_active = get_api_status()

    return json.dumps(
        {
            "defineConstant": {
                name.upper(): is_active
                for name, is_active in apis_active.items()
            },
        },
    )


def generate_pyright_config_toml():
    """Generate a Pyright config to be used in `pyproject.toml`."""
    apis_active = get_api_status()

    return "[tool.pyright.defineConstant]\n" + "\n".join(
        f"{name.upper()} = {str(is_active).lower()}"
        for name, is_active in apis_active.items()
    )


def print_mypy_args():
    """Print the generated mypy args to stdout."""
    print(generate_mypy_args())


def print_pyright_config_json():
    """Print the generated Pyright JSON config to stdout."""
    print(generate_pyright_config_json())


def print_pyright_config_toml():
    """Print the generated Pyright TOML config to stdout."""
    print(generate_pyright_config_toml())


def print_pyright_configs():
    """Print the generated Pyright configs to stdout."""
    print("pyrightconfig.json:")
    print_pyright_config_json()
    print()
    print("pyproject.toml:")
    print_pyright_config_toml()


def generate_arg_parser():
    """Generate the argument parser for the dev CLI for QtPy."""
    parser = argparse.ArgumentParser(
        description="Features to support development with QtPy.",
    )
    parser.set_defaults(func=parser.print_help)

    parser.add_argument(
        "--version",
        action="store_const",
        dest="func",
        const=print_version,
        help="If passed, will print the version and exit",
    )

    cli_subparsers = parser.add_subparsers(
        title="Subcommands",
        help="Subcommand to run",
        metavar="Subcommand",
    )

    # Parser for the MyPy args subcommand
    mypy_args_parser = cli_subparsers.add_parser(
        name="mypy-args",
        help="Generate command line arguments for using mypy with QtPy.",
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent(
            """
            Generate command line arguments for using mypy with QtPy.

            This will generate strings similar to the following
            which help guide mypy through which library QtPy would have used
            so that mypy can get the proper underlying type hints.

                --always-false=PYQT5 --always-false=PYQT6 --always-true=PYSIDE2 --always-false=PYSIDE6

            It can be used as follows on Bash or a similar shell:

                mypy --package mypackage $(qtpy mypy-args)
            """,
        ),
    )
    mypy_args_parser.set_defaults(func=print_mypy_args)

    # Parser for the Pyright config subcommand
    pyright_config_parser = cli_subparsers.add_parser(
        name="pyright-config",
        help="Generate Pyright config for using Pyright with QtPy.",
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent(
            """
            Generate Pyright config for using Pyright with QtPy.

            This will generate config sections to be included in a Pyright
            config file (either `pyrightconfig.json` or `pyproject.toml`)
            which help guide Pyright through which library QtPy would have used
            so that Pyright can get the proper underlying type hints.

            """,
        ),
    )
    pyright_config_parser.set_defaults(func=print_pyright_configs)

    return parser


def main(args=None):
    """Run the development CLI for QtPy."""
    parser = generate_arg_parser()
    parsed_args = parser.parse_args(args=args)

    reserved_params = {"func"}
    cleaned_args = {
        key: value
        for key, value in vars(parsed_args).items()
        if key not in reserved_params
    }
    parsed_args.func(**cleaned_args)

"""Debugging utilities."""

from __future__ import annotations

import os
import platform
import sys
from dataclasses import dataclass
from importlib import metadata


@dataclass
class Variable:
    """Dataclass describing an environment variable."""

    name: str
    """Variable name."""
    value: str
    """Variable value."""


@dataclass
class Package:
    """Dataclass describing a Python package."""

    name: str
    """Package name."""
    version: str
    """Package version."""


@dataclass
class Environment:
    """Dataclass to store environment information."""

    interpreter_name: str
    """Python interpreter name."""
    interpreter_version: str
    """Python interpreter version."""
    interpreter_path: str
    """Path to Python executable."""
    platform: str
    """Operating System."""
    packages: list[Package]
    """Installed packages."""
    variables: list[Variable]
    """Environment variables."""


def _interpreter_name_version() -> tuple[str, str]:
    if hasattr(sys, "implementation"):
        impl = sys.implementation.version
        version = f"{impl.major}.{impl.minor}.{impl.micro}"
        kind = impl.releaselevel
        if kind != "final":
            version += kind[0] + str(impl.serial)
        return sys.implementation.name, version
    return "", "0.0.0"


def get_version(dist: str = "griffe") -> str:
    """Get version of the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        A version number.
    """
    try:
        return metadata.version(dist)
    except metadata.PackageNotFoundError:
        return "0.0.0"


def get_debug_info() -> Environment:
    """Get debug/environment information.

    Returns:
        Environment information.
    """
    py_name, py_version = _interpreter_name_version()
    packages = ["griffe"]
    variables = ["PYTHONPATH", *[var for var in os.environ if var.startswith("GRIFFE")]]
    return Environment(
        interpreter_name=py_name,
        interpreter_version=py_version,
        interpreter_path=sys.executable,
        platform=platform.platform(),
        variables=[Variable(var, val) for var in variables if (val := os.getenv(var))],
        packages=[Package(pkg, get_version(pkg)) for pkg in packages],
    )


def print_debug_info() -> None:
    """Print debug/environment information."""
    info = get_debug_info()
    print(f"- __System__: {info.platform}")
    print(f"- __Python__: {info.interpreter_name} {info.interpreter_version} ({info.interpreter_path})")
    print("- __Environment variables__:")
    for var in info.variables:
        print(f"  - `{var.name}`: `{var.value}`")
    print("- __Installed packages__:")
    for pkg in info.packages:
        print(f"  - `{pkg.name}` v{pkg.version}")


if __name__ == "__main__":
    print_debug_info()

"""Metadata for the Project."""

from __future__ import annotations

import importlib.metadata

__all__ = ["__version__", "__project__"]

__version__ = importlib.metadata.version("polyfactory")
"""Version of the project."""
__project__ = importlib.metadata.metadata("polyfactory")["Name"]
"""Name of the project."""

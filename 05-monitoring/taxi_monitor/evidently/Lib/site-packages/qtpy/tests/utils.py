"""Utility functions for tests."""

import os


def using_conda():
    return os.environ.get("USE_CONDA", "Yes") == "Yes"


def not_using_conda():
    return os.environ.get("USE_CONDA", "No") == "No"

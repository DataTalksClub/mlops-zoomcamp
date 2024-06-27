# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides Qsci classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtBindingMissingModuleError,
    QtModuleNotInstalledError,
)

if PYQT5:
    try:
        from PyQt5.Qsci import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="Qsci",
            missing_package="QScintilla",
        ) from error
elif PYQT6:
    try:
        from PyQt6.Qsci import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="Qsci",
            missing_package="PyQt6-QScintilla",
        ) from error
elif PYSIDE2 or PYSIDE6:
    raise QtBindingMissingModuleError(name="Qsci")

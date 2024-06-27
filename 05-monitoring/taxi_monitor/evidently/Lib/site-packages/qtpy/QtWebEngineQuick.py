# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtWebEngineQuick classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtBindingMissingModuleError,
    QtModuleNotInstalledError,
)

if PYQT5:
    raise QtBindingMissingModuleError(name="QtWebEngineQuick")
elif PYQT6:
    try:
        from PyQt6.QtWebEngineQuick import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtWebEngineQuick",
            missing_package="PyQt6-WebEngine",
        ) from error
elif PYSIDE2:
    raise QtBindingMissingModuleError(name="QtWebEngineQuick")
elif PYSIDE6:
    from PySide6.QtWebEngineQuick import *

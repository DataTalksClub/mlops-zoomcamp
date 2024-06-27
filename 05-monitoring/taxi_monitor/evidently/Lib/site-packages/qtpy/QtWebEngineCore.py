# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtWebEngineCore classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtModuleNotInstalledError,
)

if PYQT5:
    try:
        from PyQt5.QtWebEngineCore import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtWebEngineCore",
            missing_package="PyQtWebEngine",
        ) from error
elif PYQT6:
    try:
        from PyQt6.QtWebEngineCore import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtWebEngineCore",
            missing_package="PyQt6-WebEngine",
        ) from error
elif PYSIDE2:
    from PySide2.QtWebEngineCore import *
elif PYSIDE6:
    from PySide6.QtWebEngineCore import *

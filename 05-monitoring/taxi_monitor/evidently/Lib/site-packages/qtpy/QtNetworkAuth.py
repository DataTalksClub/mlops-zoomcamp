# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtNetworkAuth classes and functions."""

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
        from PyQt5.QtNetworkAuth import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtNetworkAuth",
            missing_package="PyQtNetworkAuth",
        ) from error
elif PYQT6:
    try:
        from PyQt6.QtNetworkAuth import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtNetworkAuth",
            missing_package="PyQt6-NetworkAuth",
        ) from error
elif PYSIDE2:
    raise QtBindingMissingModuleError(name="QtNetworkAuth")
elif PYSIDE6:
    from PySide6.QtNetworkAuth import *

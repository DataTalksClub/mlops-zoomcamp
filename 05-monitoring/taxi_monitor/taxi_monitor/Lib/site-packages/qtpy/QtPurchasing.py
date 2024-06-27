# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtPurchasing classes and functions."""

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
        from PyQt5.QtPurchasing import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtPurchasing",
            missing_package="PyQtPurchasing",
        ) from error
elif PYQT6 or PYSIDE2 or PYSIDE6:
    raise QtBindingMissingModuleError(name="QtPurchasing")

# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtBluetooth classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtBindingMissingModuleError,
)

if PYQT5:
    from PyQt5.QtBluetooth import *
elif PYQT6:
    from PyQt6.QtBluetooth import *
elif PYSIDE2:
    raise QtBindingMissingModuleError(name="QtBluetooth")
elif PYSIDE6:
    from PySide6.QtBluetooth import *

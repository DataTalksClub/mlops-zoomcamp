# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtQuick3D classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtBindingMissingModuleError,
)

if PYQT5:
    from PyQt5.QtQuick3D import *
elif PYQT6:
    from PyQt6.QtQuick3D import *
elif PYSIDE2:
    raise QtBindingMissingModuleError(name="QtQuick3D")
elif PYSIDE6:
    from PySide6.QtQuick3D import *

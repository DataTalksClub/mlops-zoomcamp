# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtSvgWidgets classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtBindingMissingModuleError,
)

if PYQT5:
    raise QtBindingMissingModuleError(name="QtSvgWidgets")
elif PYQT6:
    from PyQt6.QtSvgWidgets import *
elif PYSIDE2:
    raise QtBindingMissingModuleError(name="QtSvgWidgets")
elif PYSIDE6:
    from PySide6.QtSvgWidgets import *

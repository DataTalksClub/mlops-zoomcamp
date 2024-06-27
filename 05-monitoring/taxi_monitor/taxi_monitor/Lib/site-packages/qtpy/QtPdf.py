# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtPdf classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtBindingMissingModuleError,
)

if PYQT5:
    raise QtBindingMissingModuleError(name="QtPdf")
elif PYQT6:
    # Available with version >=6.4.0
    from PyQt6.QtPdf import *
elif PYSIDE2:
    raise QtBindingMissingModuleError(name="QtPdf")
elif PYSIDE6:
    # Available with version >=6.4.0
    from PySide6.QtPdf import *

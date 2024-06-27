# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtDBus classes and functions."""

import sys

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtBindingMissingModuleError,
    QtModuleNotInOSError,
)

if PYQT5:
    from PyQt5.QtDBus import *
elif PYQT6:
    from PyQt6.QtDBus import *
elif PYSIDE2:
    raise QtBindingMissingModuleError(name="QtDBus")
elif PYSIDE6:
    if sys.platform != "win32":
        from PySide6.QtDBus import *
    else:
        raise QtModuleNotInOSError(name="QtDBus")

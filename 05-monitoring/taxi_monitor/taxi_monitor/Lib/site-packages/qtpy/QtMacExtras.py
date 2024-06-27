# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides classes and functions specific to macOS and iOS operating systems"""

import sys

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtModuleNotInOSError,
    QtModuleNotInQtVersionError,
)

if sys.platform == "darwin":
    if PYQT5:
        from PyQt5.QtMacExtras import *
    elif PYQT6:
        raise QtModuleNotInQtVersionError(name="QtMacExtras")
    elif PYSIDE2:
        from PySide2.QtMacExtras import *
    elif PYSIDE6:
        raise QtModuleNotInQtVersionError(name="QtMacExtras")
else:
    raise QtModuleNotInOSError(name="QtMacExtras")

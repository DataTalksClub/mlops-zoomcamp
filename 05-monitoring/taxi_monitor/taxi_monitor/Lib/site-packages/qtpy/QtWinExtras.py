# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides Windows-specific utilities"""

import sys

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtModuleNotInOSError,
    QtModuleNotInQtVersionError,
)

if sys.platform == "win32":
    if PYQT5:
        from PyQt5.QtWinExtras import *
    elif PYQT6:
        raise QtModuleNotInQtVersionError(name="QtWinExtras")
    elif PYSIDE2:
        from PySide2.QtWinExtras import *
    elif PYSIDE6:
        raise QtModuleNotInQtVersionError(name="QtWinExtras")
else:
    raise QtModuleNotInOSError(name="QtWinExtras")

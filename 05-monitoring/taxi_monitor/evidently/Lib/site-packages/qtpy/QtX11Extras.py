# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides Linux-specific utilities"""

import sys

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtModuleNotInOSError,
    QtModuleNotInQtVersionError,
)

if sys.platform == "linux":
    if PYQT5:
        from PyQt5.QtX11Extras import *
    elif PYQT6:
        raise QtModuleNotInQtVersionError(name="QtX11Extras")
    elif PYSIDE2:
        from PySide2.QtX11Extras import *
    elif PYSIDE6:
        raise QtModuleNotInQtVersionError(name="QtX11Extras")
else:
    raise QtModuleNotInOSError(name="QtX11Extras")

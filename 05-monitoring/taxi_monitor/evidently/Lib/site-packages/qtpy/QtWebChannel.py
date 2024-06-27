# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtWebChannel classes and functions."""

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6

if PYQT5:
    from PyQt5.QtWebChannel import *
elif PYQT6:
    from PyQt6.QtWebChannel import *
elif PYSIDE2:
    from PySide2.QtWebChannel import *
elif PYSIDE6:
    from PySide6.QtWebChannel import *

# -----------------------------------------------------------------------------
# Copyright 2020 Antonio Valentino
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtPositioning classes and functions."""

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6

if PYQT5:
    from PyQt5.QtPositioning import *
elif PYQT6:
    from PyQt6.QtPositioning import *
elif PYSIDE2:
    from PySide2.QtPositioning import *
elif PYSIDE6:
    from PySide6.QtPositioning import *

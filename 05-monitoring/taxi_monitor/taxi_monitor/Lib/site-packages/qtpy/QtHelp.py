# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""QtHelp Wrapper."""

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6

if PYQT5:
    from PyQt5.QtHelp import *
elif PYQT6:
    from PyQt6.QtHelp import *
elif PYSIDE2:
    from PySide2.QtHelp import *
elif PYSIDE6:
    from PySide6.QtHelp import *

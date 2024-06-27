# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtStateMachine classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtBindingMissingModuleError,
)

if PYQT5 or PYQT6 or PYSIDE2:
    raise QtBindingMissingModuleError(name="QtStateMachine")
elif PYSIDE6:
    from PySide6.QtStateMachine import *

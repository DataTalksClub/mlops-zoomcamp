# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtTextToSpeech classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtBindingMissingModuleError,
)

if PYQT5:
    from PyQt5.QtTextToSpeech import *
elif PYQT6:
    raise QtBindingMissingModuleError(name="QtTextToSpeech")
elif PYSIDE2:
    from PySide2.QtTextToSpeech import *
elif PYSIDE6:
    raise QtBindingMissingModuleError(name="QtTextToSpeech")

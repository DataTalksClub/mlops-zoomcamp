# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides access to shiboken."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtBindingMissingModuleError,
)

if PYQT5 or PYQT6:
    raise QtBindingMissingModuleError(name="shiboken")
elif PYSIDE2:
    from shiboken2 import *
elif PYSIDE6:
    from shiboken6 import *

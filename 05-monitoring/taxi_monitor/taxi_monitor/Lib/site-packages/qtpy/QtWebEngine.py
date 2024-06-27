# -----------------------------------------------------------------------------
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009- The Spyder development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtWebEngine classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtModuleNotInQtVersionError,
    QtModuleNotInstalledError,
)

if PYQT5:
    try:
        from PyQt5.QtWebEngine import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtWebEngine",
            missing_package="PyQtWebEngine",
        ) from error
elif PYQT6:
    raise QtModuleNotInQtVersionError(name="QtWebEngine")
elif PYSIDE2:
    from PySide2.QtWebEngine import *
elif PYSIDE6:
    raise QtModuleNotInQtVersionError(name="QtWebEngine")

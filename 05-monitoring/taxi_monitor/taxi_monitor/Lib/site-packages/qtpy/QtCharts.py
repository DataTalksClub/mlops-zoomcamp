# -----------------------------------------------------------------------------
# Copyright © 2019- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------

"""Provides QtChart classes and functions."""

from . import (
    PYQT5,
    PYQT6,
    PYSIDE2,
    PYSIDE6,
    QtModuleNotInstalledError,
)

if PYQT5:
    try:
        from PyQt5 import QtChart as QtCharts
        from PyQt5.QtChart import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtCharts",
            missing_package="PyQtChart",
        ) from error
elif PYQT6:
    try:
        from PyQt6 import QtCharts
        from PyQt6.QtCharts import *
    except ModuleNotFoundError as error:
        raise QtModuleNotInstalledError(
            name="QtCharts",
            missing_package="PyQt6-Charts",
        ) from error
elif PYSIDE2:
    import inspect

    # https://bugreports.qt.io/projects/PYSIDE/issues/PYSIDE-1026
    import PySide2.QtCharts as __temp
    from PySide2.QtCharts import *

    for __name in inspect.getmembers(__temp.QtCharts):
        globals()[__name[0]] = __name[1]
elif PYSIDE6:
    from PySide6 import QtCharts
    from PySide6.QtCharts import *
